# DIZZY DEDUPE

The dedupe application is organized into stage-based folders that mirror the data processing lifecycle:

## Directory Structure

- `def/` - Definitions and schemas
- `gen/` - Code generation and derived artifacts
- `deploy/` - Deployment configurations and infrastructure as code
- `queries/` - Database and data query operations
- `procedures/` - Reusable procedures and workflows
- `policies/` - Policy definitions and enforcement
- `mutations/` - Data transformation operations
- `tests/` - Test suites

## Pulumi Deployment

The `deploy/` directory contains a Pulumi stack for deploying Minio object storage to Kubernetes.

### Prerequisites

- Pulumi CLI installed
- kubectl configured with access to your Kubernetes cluster
- Python 3.10+ with uv package manager

### Deployment

1. Navigate to the deploy directory:
```bash
cd app/dedupe/deploy
```

2. Install dependencies:
```bash
pulumi install
```

3. Configure secrets (required):
```bash
pulumi config set --secret minio:minio_user "admin"
pulumi config set --secret minio:minio_password "your-secure-password"
```

4. Set your kubeconfig (if not default):
```bash
export KUBECONFIG=/path/to/your/kubeconfig
```

5. Deploy the stack:
```bash
pulumi up
```

### What Gets Deployed

The Pulumi stack creates:
- A `minio` namespace in Kubernetes
- A Minio deployment with:
  - API endpoint on port 9000 (NodePort 30000)
  - Console UI on port 9001 (NodePort 30001)
  - Persistent storage mounted from host path `/mnt/win/minio`
- A Kubernetes service exposing Minio via NodePort

### Verification

After deployment, verify the stack:

1. Check Pulumi outputs:
```bash
pulumi stack output
```

Expected outputs:
- `minio_endpoint: localhost:30000`
- `minio_console: localhost:30001`

2. Verify Kubernetes resources:
```bash
kubectl get all -n minio
```

3. Access the Minio console:
   - Open browser to `http://localhost:30001`
   - Login with the credentials configured in step 3

4. Test API connectivity:
```bash
curl http://localhost:30000/minio/health/live
```

### Cleanup

To remove the deployment:
```bash
pulumi destroy
```

