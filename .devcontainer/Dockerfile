FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

ARG KUBECTL_VERSION=v1.32.0
ARG HELM_VERSION=v3.17.0
ARG K3D_VERSION=v5.7.3
ARG TASK_VERSION=v3.41.0
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

# Install Jumpstarter CLI
RUN pip3 install --no-cache-dir "jumpstarter==${JUMPSTARTER_VERSION}" || \
    pip3 install --no-cache-dir jumpstarter

# Enable shell completion
RUN kubectl completion bash > /etc/bash_completion.d/kubectl \
    && helm completion bash > /etc/bash_completion.d/helm

USER vscode
