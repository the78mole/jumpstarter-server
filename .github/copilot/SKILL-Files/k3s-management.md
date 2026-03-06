# K3s / k3d Management — SKILL File

Troubleshooting and maintenance steps for the local K3s environment running via k3d.

---

## Quick Reference

| Action               | Command                            |
|----------------------|------------------------------------|
| Create cluster       | `task cluster:create`              |
| Delete cluster       | `task cluster:delete`              |
| Start stopped cluster| `task cluster:start`               |
| Stop cluster         | `task cluster:stop`                |
| Full setup           | `task setup`                       |
| Full teardown        | `task clean`                       |

---

## Cluster Lifecycle

### Create cluster from config

```bash
k3d cluster create --config k3d-config.yaml
```

### List clusters

```bash
k3d cluster list
```

### Get kubeconfig

```bash
k3d kubeconfig get jumpstarter > ~/.kube/config
# Or merge into existing kubeconfig:
k3d kubeconfig merge jumpstarter --kubeconfig-merge-default
```

### Delete cluster

```bash
k3d cluster delete jumpstarter
```

---

## Node Troubleshooting

### List nodes

```bash
kubectl get nodes -o wide
```

### Node not Ready

```bash
# Check node conditions
kubectl describe node <node-name>

# Restart the k3d node container
docker restart k3d-jumpstarter-server-0
```

### Drain and cordon a node

```bash
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data
kubectl uncordon <node-name>
```

---

## Pod Troubleshooting

### Pods in Pending state

```bash
# Check events
kubectl get events -n <namespace> --sort-by='.lastTimestamp'

# Describe the pod
kubectl describe pod -n <namespace> <pod-name>
```

### Pods in CrashLoopBackOff

```bash
# View current logs
kubectl logs -n <namespace> <pod-name>

# View previous container logs (after crash)
kubectl logs -n <namespace> <pod-name> --previous
```

### Exec into a running pod

```bash
kubectl exec -it -n <namespace> <pod-name> -- /bin/sh
```

---

## Networking Troubleshooting

### Check k3d port mappings

```bash
k3d cluster list --no-headers
docker ps --filter name=k3d-jumpstarter
```

### Verify LoadBalancer service

```bash
kubectl get svc -A | grep LoadBalancer
```

### Test connectivity to a service from inside the cluster

```bash
# Run a temporary debug pod
kubectl run debug --rm -it --image=nicolaka/netshoot -- /bin/bash

# Inside the pod:
curl -v http://<service-name>.<namespace>.svc.cluster.local:<port>
```

### DNS resolution check

```bash
kubectl run debug --rm -it --image=busybox:1.36 -- nslookup kubernetes.default
```

---

## Storage Troubleshooting

### List PersistentVolumeClaims

```bash
kubectl get pvc -A
```

### PVC stuck in Pending

```bash
kubectl describe pvc -n <namespace> <pvc-name>
# k3d uses 'local-path' provisioner by default
kubectl get storageclass
```

---

## Ingress / Traefik Troubleshooting

### Check Traefik pods

```bash
kubectl get pods -n traefik
kubectl logs -n traefik -l app.kubernetes.io/name=traefik -f
```

### Verify IngressRoute / Ingress objects

```bash
kubectl get ingress -A
kubectl describe ingress -n jumpstarter jumpstarter
```

### Test gRPC through Traefik

```bash
# grpcurl must be installed; -insecure bypasses self-signed cert check
grpcurl -insecure localhost:8082 list
```

---

## cert-manager Troubleshooting

### Check ClusterIssuers

```bash
kubectl get clusterissuer
kubectl describe clusterissuer selfsigned-issuer
```

### Check Certificates and CertificateRequests

```bash
kubectl get certificate -A
kubectl get certificaterequest -A
kubectl describe certificate -n jumpstarter jumpstarter-tls
```

### Common cert-manager issues

| Symptom                      | Fix                                                  |
|------------------------------|------------------------------------------------------|
| Certificate stuck `Issuing`  | Check `CertificateRequest` events and `cert-manager` logs |
| `ClusterIssuer` not ready    | Re-apply `helm/cert-manager/cluster-issuer.yaml`     |
| TLS secret missing           | Delete and let cert-manager re-issue                 |

---

## Helm Troubleshooting

### List all installed releases

```bash
helm list -A
```

### Inspect a failed release

```bash
helm status -n <namespace> <release-name>
helm get manifest -n <namespace> <release-name>
```

### Rollback a release

```bash
helm rollback -n <namespace> <release-name> <revision>
```

---

## Registry Troubleshooting

### Check k3d local registry

```bash
curl http://localhost:5111/v2/_catalog
```

### Push image to registry

```bash
task registry:push IMAGE=myimage:tag
# Equivalent to:
docker tag myimage:tag localhost:5111/myimage:tag
docker push localhost:5111/myimage:tag
```

---

## Complete Reset

If the cluster is in an unrecoverable state:

```bash
task clean        # deletes the k3d cluster
task setup        # recreates everything from scratch
```
