# jumpstarter-server

A **Jumpstarter-in-a-Box** environment that packages the
[Jumpstarter](https://jumpstarter.dev) server-side components into a local
"Mini-Cluster" using **K3s via k3d** and **Docker**.
The environment runs entirely inside a VS Code DevContainer and is fully
operational after a single `task setup` command.

---

## Quick Start

### Prerequisites

- [VS Code](https://code.visualstudio.com/) with the
  [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- Docker Desktop (or Docker Engine) running on the host

### One-Click Setup

1. Clone this repository and open it in VS Code.
2. When prompted, click **Reopen in Container**.
3. The DevContainer builds and automatically runs `task setup`.
4. Once complete, the cluster is ready:
   - Jumpstarter Controller gRPC: `localhost:8082`
   - Jumpstarter Router gRPC:     `localhost:8083`
   - K3s API Server:              `localhost:6443`

---

## Manual Setup

If you prefer to set up outside the DevContainer (requires `kubectl`, `helm`,
`k3d`, and `task` on your PATH):

```bash
# 1. Add Helm repos
task helm:repos

# 2. Create the k3d cluster
task cluster:create

# 3. Install cert-manager, Traefik, and Jumpstarter
task install:cert-manager
task install:traefik
task install:jumpstarter

# 4. Verify everything is running
task status
```

---

## Available Tasks

| Task                          | Description                                        |
|-------------------------------|----------------------------------------------------|
| `task setup`                  | Full one-click setup                               |
| `task test`                   | Run integration tests                              |
| `task clean`                  | Tear down the cluster                              |
| `task status`                 | Show nodes / pods / services                       |
| `task cluster:create`         | Create the k3d cluster                             |
| `task cluster:delete`         | Delete the k3d cluster                             |
| `task install:cert-manager`   | Install cert-manager                               |
| `task install:traefik`        | Install Traefik v2 ingress                         |
| `task install:jumpstarter`    | Install Jumpstarter controller + router            |
| `task logs:controller`        | Tail Jumpstarter controller logs                   |
| `task logs:router`            | Tail Jumpstarter router logs                       |
| `task registry:push IMAGE=…`  | Push local image to k3d registry                  |

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    VS Code DevContainer                  │
│                                                          │
│  ┌───────────────────────────────────────────────────┐   │
│  │               k3d (K3s in Docker)                 │   │
│  │                                                   │   │
│  │  ┌────────────┐  ┌──────────────┐  ┌──────────┐  │   │
│  │  │ cert-mgr   │  │  Traefik v2  │  │  Jumpst. │  │   │
│  │  │ (mTLS/TLS) │  │  gRPC/HTTP2  │  │Controller│  │   │
│  │  └────────────┘  └──────────────┘  │  :8082   │  │   │
│  │                                    ├──────────┤  │   │
│  │                                    │  Router  │  │   │
│  │                                    │  :8083   │  │   │
│  └───────────────────────────────────────────────────┘   │
│                         │                               │
│           Docker socket (DooD)                          │
└──────────────────────────────────────────────────────────┘
```

## Port Mappings

| Port  | Service                      | Protocol      |
|-------|------------------------------|---------------|
| 6443  | K3s API Server               | HTTPS         |
| 8080  | Traefik HTTP entrypoint      | HTTP          |
| 8082  | Jumpstarter Controller gRPC  | gRPC (HTTP/2) |
| 8083  | Jumpstarter Router gRPC      | gRPC (HTTP/2) |
| 5111  | k3d local image registry     | HTTP          |

---

## Repository Structure

```
jumpstarter-server/
├── .devcontainer/
│   ├── devcontainer.json        # DevContainer (DooD, extensions, auto-setup)
│   └── Dockerfile               # kubectl, helm, k3d, task, jumpstarter CLI
├── .github/
│   ├── copilot/SKILL-Files/
│   │   ├── jumpstarter-ops.md   # Controller management commands
│   │   └── k3s-management.md   # K3s / k3d troubleshooting
│   └── workflows/
│       ├── ci.yml               # Integration tests CI
│       └── release.yml          # Semantic-version release
├── helm/
│   ├── cert-manager/            # cert-manager values + ClusterIssuer
│   ├── jumpstarter/             # Jumpstarter Helm values
│   └── traefik/                 # Traefik v2 Helm values
├── scripts/
│   └── test_integration.py      # Python integration tests
├── copilot_instructions.md      # AI context: architecture & workflows
├── k3d-config.yaml              # k3d cluster definition
├── Taskfile.yaml                # Automation tasks
└── README.md
```

---

## CI/CD

- **Integration tests** run on every push and pull request to `main` via
  `.github/workflows/ci.yml`.
- **Releases** are created automatically on merge to `main` using
  [paulhatch/semantic-version](https://github.com/paulhatch/semantic-version)
  in `.github/workflows/release.yml`.

### Conventional Commits

| Commit message contains | Version bump |
|-------------------------|-------------|
| `(MAJOR)`               | Major        |
| `(MINOR)`               | Minor        |
| Everything else         | Patch        |

> All conventional-commit prefixes (`fix:`, `feat:`, `chore:`, etc.) result in
> a **patch** bump unless the message also contains `(MAJOR)` or `(MINOR)`.
> To trigger a minor bump for a new feature, add `(MINOR)` to the commit body.

---

## References

- [Jumpstarter documentation](https://jumpstarter.dev)
- [k3d documentation](https://k3d.io)
- [Taskfile documentation](https://taskfile.dev)
- [cert-manager documentation](https://cert-manager.io)
- [Traefik documentation](https://doc.traefik.io/traefik/)

