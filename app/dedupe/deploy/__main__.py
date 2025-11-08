# __main__.py
import pulumi
# import pulumi_docker as docker
import pulumi_kubernetes as k8s
import pulumi_tailscale as tailscale

# Pull secrets
config = pulumi.Config("minio")
root_user = config.require_secret("minio_user")
root_password = config.require_secret("minio_password")

# Tailscale ACL configuration (using separate namespace to avoid provider conflicts)
acl_config = pulumi.Config("minio-acl")
allowed_users = acl_config.get_object("allowed_users") or []
minio_server_tag = acl_config.get("minio_server_tag") or "tag:minio-server"

# Create namespace
namespace = k8s.core.v1.Namespace("minio-namespace",
    metadata=k8s.meta.v1.ObjectMetaArgs(name="minio")
)

# Create deployment
minio_deployment = k8s.apps.v1.Deployment("minio",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        namespace=namespace.metadata.name,
        name="minio"
    ),
    spec=k8s.apps.v1.DeploymentSpecArgs(
        replicas=1,
        selector=k8s.meta.v1.LabelSelectorArgs(
            match_labels={"app": "minio"}
        ),
        template=k8s.core.v1.PodTemplateSpecArgs(
            metadata=k8s.meta.v1.ObjectMetaArgs(
                labels={"app": "minio"}
            ),
            spec=k8s.core.v1.PodSpecArgs(
                containers=[k8s.core.v1.ContainerArgs(
                    name="minio",
                    image="minio/minio:latest",
                    command=["minio", "server", "/data", "--console-address", ":9001"],
                    env=[
                        k8s.core.v1.EnvVarArgs(name="MINIO_ROOT_USER", value=root_user),
                        k8s.core.v1.EnvVarArgs(name="MINIO_ROOT_PASSWORD", value=root_password),
                    ],
                    ports=[
                        k8s.core.v1.ContainerPortArgs(container_port=9000),
                        k8s.core.v1.ContainerPortArgs(container_port=9001),
                    ],
                    volume_mounts=[
                        k8s.core.v1.VolumeMountArgs(
                            name="data",
                            mount_path="/data"
                        )
                    ]
                )],
                volumes=[
                    k8s.core.v1.VolumeArgs(
                        name="data",
                        host_path=k8s.core.v1.HostPathVolumeSourceArgs(
                            path="/mnt/win/minio",
                            type="DirectoryOrCreate"
                        )
                    )
                ]
            )
        )
    )
)

# Create service
minio_service = k8s.core.v1.Service("minio-service",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        namespace=namespace.metadata.name,
        name="minio"
    ),
    spec=k8s.core.v1.ServiceSpecArgs(
        type="NodePort",
        selector={"app": "minio"},
        ports=[
            k8s.core.v1.ServicePortArgs(name="api", port=9000, target_port=9000, node_port=30000),
            k8s.core.v1.ServicePortArgs(name="console", port=9001, target_port=9001, node_port=30001),
        ]
    )
)

pulumi.export("minio_endpoint", "localhost:30000")
pulumi.export("minio_console", "localhost:30001")

# Tailscale ACL to control access to MinIO on hjelm
if allowed_users:
    # Create ACL policy - preserve existing behavior with wildcard grants
    # and just update the tag owners for minio-open
    acl_policy = {
        "tagOwners": {
            minio_server_tag: allowed_users
        },
        "grants": [
            # Allow all connections (preserving default behavior)
            {
                "src": ["*"],
                "dst": ["*"],
                "ip": ["*"]
            }
        ],
        "ssh": [
            # Allow all users to SSH into their own devices in check mode
            {
                "action": "check",
                "src": ["autogroup:member"],
                "dst": ["autogroup:self"],
                "users": ["autogroup:nonroot", "root"]
            }
        ]
    }

    # Apply ACL
    tailscale_acl = tailscale.Acl("minio-access",
        acl=pulumi.Output.json_dumps(acl_policy),
        opts=pulumi.ResourceOptions(protect=True)
    )

    pulumi.export("tailscale_acl_configured", True)
    pulumi.export("minio_allowed_users_count", len(allowed_users))
    pulumi.export("minio_server_tag", minio_server_tag)
else:
    pulumi.export("tailscale_acl_configured", False)