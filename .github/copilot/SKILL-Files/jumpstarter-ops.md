# Jumpstarter Operations — SKILL File

Reference commands for managing the Jumpstarter controller and router in the local k3d environment.

---

## Namespaces

All Jumpstarter components are deployed in the `jumpstarter` namespace.

```bash
kubectl get all -n jumpstarter
```

---

## Controller Management

### Check controller status

```bash
kubectl get deploy -n jumpstarter
kubectl get pods -n jumpstarter -l app.kubernetes.io/name=jumpstarter-controller
```

### Tail controller logs

```bash
kubectl logs -n jumpstarter -l app.kubernetes.io/name=jumpstarter-controller -f
# Or via Taskfile:
task logs:controller
```

### Restart controller

```bash
kubectl rollout restart deployment/jumpstarter-controller -n jumpstarter
kubectl rollout status deployment/jumpstarter-controller -n jumpstarter
```

### Describe controller pod (debug crashes)

```bash
kubectl describe pod -n jumpstarter \
  $(kubectl get pods -n jumpstarter -l app.kubernetes.io/name=jumpstarter-controller \
    -o jsonpath='{.items[0].metadata.name}')
```

---

## Router Management

### Check router status

```bash
kubectl get pods -n jumpstarter -l app.kubernetes.io/name=jumpstarter-router
```

### Tail router logs

```bash
kubectl logs -n jumpstarter -l app.kubernetes.io/name=jumpstarter-router -f
# Or via Taskfile:
task logs:router
```

### Restart router

```bash
kubectl rollout restart deployment/jumpstarter-router -n jumpstarter
```

---

## gRPC Endpoint Verification

The controller exposes its gRPC API on **port 8082** (forwarded to localhost via k3d).

### Check port is open

```bash
nc -zv localhost 8082
```

### List gRPC services with grpcurl

```bash
grpcurl -plaintext localhost:8082 list
```

### Jumpstarter CLI health check

```bash
# Set the endpoint
export JUMPSTARTER_GRPC_ENDPOINT=localhost:8082

# List available exporters (requires a valid client config)
jmpctl get exporters
```

---

## Helm Release Management

### Show installed release

```bash
helm list -n jumpstarter
```

### Upgrade Jumpstarter chart

```bash
helm upgrade jumpstarter jumpstarter/jumpstarter \
  --namespace jumpstarter \
  --values helm/jumpstarter/values.yaml \
  --wait
```

### Uninstall Jumpstarter

```bash
helm uninstall jumpstarter -n jumpstarter
```

---

## TLS / cert-manager

### Check issued certificates

```bash
kubectl get certificate -n jumpstarter
kubectl describe certificate jumpstarter-tls -n jumpstarter
```

### Force certificate renewal

```bash
kubectl delete secret jumpstarter-tls -n jumpstarter
# cert-manager will automatically re-issue within ~30 s
```

---

## Common Error Patterns

| Symptom                              | Likely Cause                          | Fix                                          |
|--------------------------------------|---------------------------------------|----------------------------------------------|
| Pod stuck in `Pending`               | Insufficient resources                | `kubectl describe pod -n jumpstarter <pod>`  |
| `CrashLoopBackOff` on controller     | Missing config / OIDC misconfiguration| Check logs with `task logs:controller`       |
| `UNAVAILABLE` on gRPC calls          | TLS cert not yet issued               | Wait and check `kubectl get certificate`     |
| `Connection refused` on port 8082    | k3d port mapping not active           | `k3d cluster list` and verify port forwards  |
