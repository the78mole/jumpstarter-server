FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

ARG KUBECTL_VERSION=v1.32.0
ARG HELM_VERSION=v3.17.0
ARG K3D_VERSION=v5.7.3
ARG TASK_VERSION=v3.41.0
ARG K9S_VERSION=v0.50.18
ARG JUMPSTARTER_VERSION=0.7.4

# Install core dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    gnupg \
    lsb-release \
    git \
    jq \
    python3 \
    python3-pip \
    python3-venv \
    bash-completion \
    && rm -rf /var/lib/apt/lists/*

# Install kubectl
RUN curl -fsSL "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl" \
    -o /usr/local/bin/kubectl \
    && chmod +x /usr/local/bin/kubectl

# Install Helm
RUN curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | \
    DESIRED_VERSION="${HELM_VERSION}" bash

# Install k3d
RUN curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | \
    TAG="${K3D_VERSION}" bash

# Install Task (Taskfile runner)
RUN curl -fsSL https://taskfile.dev/install.sh | \
    sh -s -- -b /usr/local/bin "${TASK_VERSION}"

# Install k9s (Kubernetes TUI)
RUN curl -fsSL "https://github.com/derailed/k9s/releases/download/${K9S_VERSION}/k9s_Linux_amd64.tar.gz" \
    | tar xz -C /usr/local/bin k9s \
    && chmod +x /usr/local/bin/k9s

# Install Jumpstarter CLI
# --break-system-packages is required on Ubuntu 24.04 (PEP 668) and is safe inside a container
RUN pip3 install --no-cache-dir --break-system-packages --extra-index-url https://pkg.jumpstarter.dev/ "jumpstarter-all==${JUMPSTARTER_VERSION}" || \
    pip3 install --no-cache-dir --break-system-packages --extra-index-url https://pkg.jumpstarter.dev/ jumpstarter-all

# Enable shell completion
RUN kubectl completion bash > /etc/bash_completion.d/kubectl \
    && helm completion bash > /etc/bash_completion.d/helm \
    && k9s completion bash > /etc/bash_completion.d/k9s

USER vscode

# k9s configuration: skin + namespace shortcuts
RUN mkdir -p ~/.config/k9s \
    && cat > ~/.config/k9s/config.yaml << 'EOF'
k9s:
  # Start in the jumpstarter namespace by default
  namespace:
    active: jumpstarter
    favorites:
      - jumpstarter
      - cert-manager
      - traefik
      - default
      - all
  # Refresh every 2 seconds
  refreshRate: 2
  # Show cluster/namespace info in header
  ui:
    headless: false
    logoless: false
    enableMouse: false
    crumbsless: false
  # Skip the confirmation prompt for non-destructive commands
  skipLatestRevCheck: true
EOF
