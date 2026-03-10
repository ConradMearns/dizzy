# Local Serverless Cloud Infrastructure with Pulumi

## Context

This project demonstrates building a complete local "cloud" infrastructure using Pulumi to orchestrate Kubernetes-based services. The goal is to show how organizations can replicate cloud-like serverless capabilities on-premises using open-source tools:

- **OpenFaaS**: Serverless function execution with auto-scaling
- **RabbitMQ**: Enterprise message queue for event-driven workflows
- **MinIO**: S3-compatible object storage
- **Local Kubernetes**: Running on the user's local k8s cluster (KinD, k3s, minikube, etc.)

This serves as a reference implementation for building custom serverless platforms without vendor lock-in, suitable for edge computing, air-gapped environments, or development workflows.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Local Kubernetes Cluster                  │
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   RabbitMQ   │◄───┤   OpenFaaS   │───►│    MinIO     │  │
│  │   Operator   │    │   Functions  │    │   Storage    │  │
│  │              │    │              │    │              │  │
│  │  Port 30673  │    │  Port 31112  │    │  Port 30900  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                    │          │
│         └────────────────────┴────────────────────┘          │
│                    Integration Layer                         │
└─────────────────────────────────────────────────────────────┘
```

**Example Data Flow**:
1. User uploads file via HTTP → OpenFaaS `upload-to-minio` function
2. Function stores file in MinIO `input` bucket
3. Function publishes message to RabbitMQ `tasks` queue
4. RabbitMQ connector triggers OpenFaaS `process-from-queue` function
5. Function downloads from MinIO, processes, uploads to `output` bucket

## Project Structure

```
pt/
├── __main__.py                    # Main Pulumi program - orchestrates all components
├── Pulumi.yaml                    # Project config with UV toolchain
├── pyproject.toml                 # Dependencies: pulumi-kubernetes, pulumi-random
├── README.md                      # Setup guide and documentation
│
├── components/                    # Reusable Pulumi ComponentResources
│   ├── __init__.py
│   ├── rabbitmq.py               # RabbitMQ operator + cluster deployment
│   ├── minio.py                  # MinIO Helm chart + bucket initialization
│   ├── openfaas.py               # OpenFaaS Helm chart + gateway setup
│   └── integration.py            # Wires components together, deploys functions
│
├── functions/                     # OpenFaaS function definitions
│   ├── process-from-queue/
│   │   ├── handler.py            # Processes files from MinIO based on queue msgs
│   │   ├── requirements.txt      # minio, pika
│   │   └── stack.yml             # Function metadata with RabbitMQ topic binding
│   └── upload-to-minio/
│       ├── handler.py            # Accepts HTTP uploads, stores in MinIO
│       ├── requirements.txt
│       └── stack.yml
│
├── docs/                          # Cached Pulumi documentation
│   ├── pulumi-kubernetes.md
│   ├── pulumi-python-uv.md
│   ├── rabbitmq-k8s-operator.md
│   ├── openfaas-k8s.md
│   └── minio-k8s.md
│
└── scripts/
    ├── setup-prereqs.sh          # Verify kubectl, pulumi, uv installed
    ├── verify-stack.sh           # End-to-end testing script
    └── cleanup.sh                # Destroy resources and clean up
```

## Implementation Plan

### Phase 1: Project Foundation

**1.1 Create project files**
- `pyproject.toml`: Dependencies for Pulumi providers
  - `pulumi>=3.206.0`
  - `pulumi-kubernetes>=4.24.0`
  - `pulumi-random>=4.16.0` (for password generation)
  - `pyyaml>=6.0.1`
- `Pulumi.yaml`: Configure UV as toolchain, set project metadata
- `README.md`: Prerequisites, quick start, architecture diagram
- Initialize UV virtual environment and install dependencies

**1.2 Cache documentation**
Create `docs/` directory with the fetched Pulumi documentation for reference:
- Pulumi Kubernetes provider overview
- Pulumi Python with UV guide
- RabbitMQ Kubernetes operator quickstart
- OpenFaaS Kubernetes deployment
- MinIO Kubernetes deployment

### Phase 2: Component Resources

**2.1 RabbitMQ Component** (`components/rabbitmq.py`)

**Resources created**:
- Apply RabbitMQ Cluster Operator manifest from GitHub release (latest)
- Create `RabbitmqCluster` custom resource (3 replicas for HA)
- Expose via NodePort on ports 30672 (AMQP), 30673 (Management UI)
- Generate admin credentials using `pulumi.Config` secrets

**Key implementation details**:
- Use `kubernetes.yaml.ConfigFile` to apply operator YAML
- Wait for CRDs using `kubernetes.apiextensions.v1.CustomResourceDefinition`
- Create cluster using `kubernetes.apiextensions.CustomResource`
- Export connection URL and credentials as outputs

**Exposed outputs**:
- `amqp_url`: Connection string for applications
- `management_url`: Web UI URL
- `admin_username`, `admin_password`: Credentials

**2.2 MinIO Component** (`components/minio.py`)

**Resources created**:
- Deploy MinIO via Helm chart (bitnami/minio or minio/minio)
- Create PersistentVolumeClaim (10Gi, configurable)
- Expose via NodePort on ports 30900 (API), 30901 (Console)
- Run initialization Job to create buckets: `input`, `output`, `archive`

**Key implementation details**:
- Use `kubernetes.helm.v3.Release` for Helm deployment
- Pass custom values for storage, credentials, NodePort config
- Create `kubernetes.batch.v1.Job` with MinIO client (`mc`) to create buckets
- Store root credentials in Pulumi config secrets

**Exposed outputs**:
- `api_url`: S3-compatible API endpoint
- `console_url`: Web console URL
- `access_key`, `secret_key`: Root credentials
- `buckets`: List of created buckets

**2.3 OpenFaaS Component** (`components/openfaas.py`)

**Resources created**:
- Create namespaces: `openfaas`, `openfaas-fn`
- Deploy OpenFaaS via Helm chart (includes NATS for async)
- Enable basic auth and generate gateway password
- Expose gateway via NodePort on port 31112

**Key implementation details**:
- Use Helm chart from `https://openfaas.github.io/faas-netes/`
- Configure async mode with NATS
- Create `kubernetes.core.v1.Secret` for basic auth
- Set resource limits for function pods

**Exposed outputs**:
- `gateway_url`: Function invocation endpoint
- `gateway_password`: Admin password for faas-cli
- `nats_url`: Internal NATS endpoint

**2.4 Integration Component** (`components/integration.py`)

**Purpose**: Wire all components together and deploy example functions

**Resources created**:
- ConfigMap with all service endpoints and credentials
- Deploy `process-from-queue` function with RabbitMQ queue binding
- Deploy `upload-to-minio` function with HTTP trigger
- Configure RabbitMQ queue: `tasks` with durable settings
- Test connectivity between all services

**Key implementation details**:
- Use `kubernetes.core.v1.ConfigMap` to share connection info
- Deploy functions using `kubernetes.apps.v1.Deployment` + `kubernetes.core.v1.Service`
- Alternatively, use OpenFaaS CRDs if preferred (`openfaas.com/v1.Function`)
- Create init container to verify all services are reachable
- Export verification status

**Exposed outputs**:
- `integration_ready`: Boolean indicating all services connected
- `test_command`: CLI command to test end-to-end flow

### Phase 3: Main Orchestration

**3.1 Main Program** (`__main__.py`)

Structure:
```python
import pulumi
from components.rabbitmq import RabbitMQComponent, RabbitMQArgs
from components.minio import MinIOComponent, MinIOArgs
from components.openfaas import OpenFaaSComponent, OpenFaaSArgs
from components.integration import IntegrationComponent

# Load configuration
config = pulumi.Config()

# Deploy infrastructure (order matters for dependencies)
rabbitmq = RabbitMQComponent("rabbitmq", RabbitMQArgs(...))
minio = MinIOComponent("minio", MinIOArgs(...))
openfaas = OpenFaaSComponent("openfaas", OpenFaaSArgs(...))

# Integrate components
integration = IntegrationComponent("integration",
    rabbitmq=rabbitmq,
    minio=minio,
    openfaas=openfaas
)

# Export all important URLs and credentials
pulumi.export("rabbitmq_management", rabbitmq.management_url)
pulumi.export("minio_console", minio.console_url)
pulumi.export("openfaas_gateway", openfaas.gateway_url)
pulumi.export("stack_ready", integration.ready)
```

**Configuration required**:
```bash
pulumi config set --secret rabbitmq_password "secure-password-123"
pulumi config set --secret minio_root_password "minio-secret-456"
```

### Phase 4: Example Functions

**4.1 process-from-queue function** (`functions/process-from-queue/`)

**handler.py** logic:
1. Parse JSON message from RabbitMQ (contains `file_path`)
2. Connect to MinIO using environment variables
3. Download file from `input` bucket
4. Process file (example: compute SHA256 hash)
5. Upload result JSON to `output` bucket
6. Return success response

**Dependencies**: `minio`, `pika` (RabbitMQ client)

**Environment variables** (injected by integration component):
- `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`
- `RABBITMQ_URL`

**4.2 upload-to-minio function** (`functions/upload-to-minio/`)

**handler.py** logic:
1. Accept file data via HTTP POST
2. Upload to MinIO `input` bucket with timestamp prefix
3. Publish message to RabbitMQ `tasks` queue with file path
4. Return confirmation with file location

**Dependencies**: `minio`, `pika`

### Phase 5: Deployment & Verification

**5.1 Setup script** (`scripts/setup-prereqs.sh`)
```bash
# Check prerequisites
- kubectl version (>= 1.19)
- Kubernetes cluster accessible (kubectl get nodes)
- Pulumi CLI installed
- UV installed (pip install uv)
- faas-cli installed (optional, for function management)

# Initialize project
uv venv .venv && source .venv/bin/activate
uv pip install -e .
```

**5.2 Deployment steps**
```bash
# Set secrets
pulumi config set --secret rabbitmq_password "YOUR_PASSWORD"
pulumi config set --secret minio_root_password "YOUR_PASSWORD"

# Deploy stack (takes ~10 minutes)
pulumi up

# Access services
kubectl port-forward -n rabbitmq-system svc/rabbitmq-cluster 15672:15672  # Optional: local access
# Or use NodePort IPs shown in pulumi outputs
```

**5.3 Verification script** (`scripts/verify-stack.sh`)
```bash
#!/bin/bash
set -e

echo "=== Verifying Local Serverless Stack ==="

# 1. Check all pods running
kubectl get pods -n rabbitmq-system | grep Running
kubectl get pods -n minio | grep Running
kubectl get pods -n openfaas | grep Running

# 2. Test RabbitMQ Management UI
curl -u admin:$RABBITMQ_PASSWORD http://localhost:30673/api/overview

# 3. Test MinIO health
curl http://localhost:30900/minio/health/live

# 4. Test OpenFaaS gateway
faas-cli list --gateway http://localhost:31112

# 5. End-to-end test
echo "test data" > /tmp/test.txt
curl -X POST http://localhost:31112/function/upload-to-minio \
  --data-binary @/tmp/test.txt

# Wait for processing
sleep 10

# Check output bucket via MinIO console or mc CLI
echo "Check MinIO console at http://localhost:30901 for output"

echo "=== All checks passed! ==="
```

## Critical Files for Implementation

1. **__main__.py** - Orchestrates component deployment and exports
2. **components/rabbitmq.py** - Most complex: CRD management, operator deployment
3. **components/minio.py** - Helm chart deployment, bucket initialization Job
4. **components/openfaas.py** - Helm deployment with NATS configuration
5. **components/integration.py** - Cross-component wiring, function deployment
6. **functions/process-from-queue/handler.py** - Demonstrates the data flow
7. **pyproject.toml** - Dependency management with UV

## Testing Strategy

**Unit tests** (optional but recommended):
- Mock component creation and verify resource specifications
- Test configuration parsing and validation
- Verify credential generation

**Integration tests** (end-to-end):
1. Deploy stack to test cluster
2. Upload file via `upload-to-minio` function
3. Verify message appears in RabbitMQ queue
4. Verify `process-from-queue` function triggered
5. Check output file exists in MinIO `output` bucket
6. Clean up test resources

## Configuration Reference

All configuration via `pulumi config`:

**Required secrets**:
- `rabbitmq_password`: Admin password for RabbitMQ
- `minio_root_password`: Root password for MinIO

**Optional settings** (with defaults):
- `rabbitmq_replicas`: 3
- `rabbitmq_storage_size`: "5Gi"
- `minio_storage_size`: "10Gi"
- `minio_buckets`: ["input", "output", "archive"]
- `openfaas_async_enabled`: true

## Resource Cleanup

```bash
# Destroy all resources
pulumi destroy

# Verify PVCs are deleted (may need manual cleanup)
kubectl get pvc --all-namespaces

# Clean up UV environment
rm -rf .venv
```

## Future Enhancements

1. **Add Prometheus/Grafana**: Monitor function metrics, queue depth, storage usage
2. **TLS Everywhere**: Secure all service communications
3. **Ingress Controller**: Replace NodePort with proper ingress
4. **CI/CD Integration**: GitHub Actions to deploy functions on git push
5. **Backup Automation**: Schedule MinIO bucket backups
6. **Multi-tenant Isolation**: Separate namespaces per "user" or "application"
7. **Cost Tracking**: Add resource labels for cost attribution
8. **Event Sourcing Example**: Demonstrate event-driven architecture patterns

## Documentation Cached

All Pulumi documentation fetched during planning is stored in `docs/` for offline reference:
- Pulumi Kubernetes provider API docs
- Pulumi Docker provider overview
- Pulumi Python with UV guide
- RabbitMQ Kubernetes operator quickstart
- OpenFaaS Kubernetes deployment guide
- MinIO Kubernetes deployment patterns

## Success Criteria

The implementation is complete when:

✅ `pulumi up` successfully deploys all components without errors
✅ All pods reach `Running` state in their respective namespaces
✅ RabbitMQ Management UI accessible at `http://localhost:30673`
✅ MinIO Console accessible at `http://localhost:30901`
✅ OpenFaaS Gateway accessible at `http://localhost:31112`
✅ End-to-end test passes: file upload → queue → processing → output
✅ `scripts/verify-stack.sh` exits with code 0
✅ Documentation in README.md is clear and complete

## Timeline Estimate

- Phase 1 (Foundation): 30 minutes
- Phase 2 (Components): 2-3 hours
- Phase 3 (Main orchestration): 30 minutes
- Phase 4 (Example functions): 1 hour
- Phase 5 (Scripts & docs): 1 hour
- **Total**: 5-6 hours of focused development
