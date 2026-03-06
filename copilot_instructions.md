# Jumpstarter-in-a-Box — Copilot Instructions

## Project Overview

This repository packages the [Jumpstarter](https://github.com/jumpstarter-dev/jumpstarter)
server-side components into a local "Mini-Cluster" using **K3s via k3d** and **Docker**.
The environment is designed to run entirely inside a VS Code DevContainer and provides a
one-click setup experience for hardware-automation testing.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     VS Code DevContainer                │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │               k3d (K3s in Docker)                │   │
│  │                                                  │   │
│  │  ┌────────────┐  ┌──────────────┐  ┌─────────┐  │   │
│  │  │ cert-mgr   │  │  Traefik v2  │  │Jumpstart│  │   │
│  │  │ (mTLS/TLS) │  │ (gRPC ingress│  │Controller│  │   │
│  │  └────────────┘  │  HTTP/2)     │  │  :8082  │  │   │
│  │                  └──────────────┘  └─────────┘  │   │
│  │                                    ┌─────────┐  │   │
│  │                                    │Jumpstart│  │   │
│  │                                    │ Router  │  │   │
│  │                                    │  :8083  │  │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                              │
│          Docker socket (DooD)                           │
└─────────────────────────────────────────────────────────┘
```

---

## Port Mappings

| Port  | Service                        | Protocol       | Notes                          |
|-------|--------------------------------|----------------|--------------------------------|
| 6443  | K3s API Server                 | HTTPS          | kubectl access                 |
| 8080  | Traefik HTTP entrypoint        | HTTP           | Redirects to HTTPS             |
| 8082  | Jumpstarter Controller         | gRPC (HTTP/2)  | Exporter → Controller comms    |
| 8083  | Jumpstarter Router             | gRPC (HTTP/2)  | Exporter ↔ Client relay        |
| 5111  | k3d local registry             | HTTP           | Push images with `task registry:push` |

---

## Directory Structure

```
jumpstarter-server/
├── .devcontainer/
│   ├── devcontainer.json     # DevContainer definition (DooD, extensions, ports)
│   └── Dockerfile            # Pre-installs kubectl, helm, k3d, task, jumpstarter CLI
├── .github/
│   ├── copilot/
│   │   └── SKILL-Files/
│   │       ├── jumpstarter-ops.md   # Jumpstarter controller management commands
│   │       └── k3s-management.md   # K3s / k3d troubleshooting steps
│   └── workflows/
│       ├── ci.yml            # Integration test workflow
│       └── release.yml       # Semantic-version release workflow
├── helm/
│   ├── cert-manager/
│   │   ├── values.yaml       # cert-manager Helm overrides
│   │   └── cluster-issuer.yaml  # Self-signed ClusterIssuer for local dev
│   ├── jumpstarter/
│   │   └── values.yaml       # Jumpstarter controller/router Helm overrides
│   └── traefik/
│       └── values.yaml       # Traefik v2 Helm overrides (gRPC/HTTP2)
├── scripts/
│   └── test_integration.py  # Python integration tests
├── copilot_instructions.md  # This file
├── k3d-config.yaml          # k3d cluster definition
├── Taskfile.yaml            # Automation: setup / test / clean
└── README.md
```

---

## Development Workflow

### One-Click Setup

1. Open the repository in VS Code.
2. When prompted, click **Reopen in Container**.
3. The DevContainer will build and then automatically run `task setup`.
4. The cluster will be ready once `task setup` completes.

### Manual steps (if needed)

```bash
# Full setup from scratch
task setup

# Run integration tests
task test

# Tear down everything
task clean

# View cluster status
task status
```

### Individual component tasks

```bash
# Recreate only Jumpstarter
task install:jumpstarter

# Tail controller logs
task logs:controller

# Tail router logs
task logs:router

# Push a local image to the k3d registry
task registry:push IMAGE=myimage:latest
```

---

## Technology Stack

| Component        | Technology                          | Version  |
|------------------|-------------------------------------|----------|
| Container runtime| Docker                              | host     |
| Local Kubernetes | K3s via k3d                         | v1.29.3  |
| Package manager  | Helm                                | v3.14.3  |
| Ingress          | Traefik v2                          | 26.1.0   |
| TLS              | cert-manager                        | v1.14.4  |
| Controller       | Jumpstarter controller              | latest   |
| Router           | Jumpstarter router                  | latest   |
| Task runner      | go-task / Taskfile                  | v3.35.1  |
| Test language    | Python 3.11                         |          |

---

## Conventional Commits

This repository uses [paulhatch/semantic-version](https://github.com/paulhatch/semantic-version)
for automated versioning. Version bumps are driven by **keywords in the commit message body**,
not by conventional-commit prefixes (e.g. `feat:`):

| Commit message contains | Version bump |
|-------------------------|-------------|
| `(MAJOR)`               | Major        |
| `(MINOR)`               | Minor        |
| Everything else         | Patch        |

> **Note:** The workflow also enables `bump_each_commit` with a
> `bump_each_commit_patch_pattern` that matches common conventional-commit
> prefixes (`fix`, `feat`, `chore`, etc.) — all of these result in a **patch**
> bump unless the message also contains `(MAJOR)` or `(MINOR)`.
> This is intentional: to trigger a minor bump for a new feature, add
> `(MINOR)` anywhere in the commit message.

---

## References

- [Jumpstarter documentation](https://jumpstarter.dev)
- [k3d documentation](https://k3d.io)
- [Taskfile documentation](https://taskfile.dev)
- [cert-manager documentation](https://cert-manager.io)
- [Traefik documentation](https://doc.traefik.io/traefik/)
