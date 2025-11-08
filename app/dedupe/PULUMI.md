```bash
pulumi new --dir ./pulumi_stacks

pulumi install

# Configure MinIO credentials
pulumi config set --secret minio:minio_user "admin"
pulumi config set --secret minio:minio_password "supersecret123"

# Configure Tailscale ACL for MinIO access control
# Get your Tailscale API key from: https://login.tailscale.com/admin/settings/keys
pulumi config set --secret tailscale:apiKey "tskey-api-xxxxx"

# Add users who should have access to MinIO on hjelm
pulumi config set --secret minio-acl:allowed_users '["alice@example.com", "bob@example.com"]'

# Optional: Set the Tailscale tag for the MinIO server (defaults to "tag:minio-server")
pulumi config set minio-acl:minio_server_tag "tag:minio-open"

# Deploy to Kubernetes
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
pulumi up
```

## Tailscale ACL Configuration

This stack configures Tailscale ACLs to control who can access your MinIO server using Tailscale tags.

### Prerequisites

Before running `pulumi up`, you need to tag the machine running MinIO (hjelm) in Tailscale:

```bash
# On the hjelm machine, or via Tailscale admin console
tailscale set --advertise-tags=tag:minio-open
```

Alternatively, tag it via the Tailscale admin console at https://login.tailscale.com/admin/machines

### How it works

- The MinIO server machine is identified by a Tailscale tag (default: `tag:minio-server`)
- Users listed in `minio-acl:allowed_users` are set as tag owners and granted access to MinIO API (port 9000) and Console (port 9001)
- All traffic stays within your Tailscale network (no Funnel required)
- Access control is declarative and version-controlled
- Changes to the user list are applied automatically on `pulumi up`

### Managing access

To add or remove users:
```bash
# Add users
pulumi config set --secret minio-acl:allowed_users '["alice@example.com", "bob@example.com", "charlie@example.com"]'

# Remove all access
pulumi config set --secret minio-acl:allowed_users '[]'

# Apply changes
pulumi up
```

### Accessing MinIO

Users with access can connect to MinIO at:
- API: `http://hjelm:9000` (or `https://hjelm.your-tailnet.ts.net:9000`)
- Console: `http://hjelm:9001` (or `https://hjelm.your-tailnet.ts.net:9001`)