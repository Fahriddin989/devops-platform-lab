# Helm workflow for devops-platform

## Release identity

- Release name: devops-platform
- Namespace: devops-lab
- Chart path: charts/devops-platform
- Values file: charts/devops-platform/values-dev.yaml

## What Helm manages

This chart manages the application layer:

- Ingress: devops-ingress
- backend Deployment, Service, ConfigMap, ServiceAccount
- frontend Deployment, Service, ServiceAccount
- redis Deployment, Service, ServiceAccount
- postgres Deployment, Service, ServiceAccount

## What Helm does not manage

These resources are intentionally outside this chart:

- backend-secret
- postgres-secret
- namespace devops-lab
- Pod Security Admission labels
- default ServiceAccount hardening manifest
- monitoring namespace
- Prometheus
- Grafana
- ingress controller
- cluster-level setup

Reason: this chart manages the application workload, not cluster bootstrap, monitoring, or secret lifecycle.

## Safe Helm workflow

Before changing the live release, run:

    make helm-check

This runs:

    helm lint
    helm template
    kubectl diff

If the diff is expected and safe, run:

    make helm-upgrade

Then verify:

    make helm-status
    make app-verify

Full release flow:

    make helm-release

Important: make helm-release performs a real helm upgrade and creates a new Helm revision even if Kubernetes diff is empty.

## Environment values

values.yaml contains default chart values.

values-dev.yaml contains local minikube overrides:

- backend image pull policy: Never
- frontend image pull policy: Never
- ingress host: app.local

Redis and Postgres use registry images and keep IfNotPresent.

## Selector policy

Current workloads still use legacy selectors:

    app: backend
    app: frontend
    app: redis
    app: postgres

Do not casually change Deployment selectors.

Reason: spec.selector is immutable for existing Deployments. Changing selectors can break Helm upgrades or detach Services from Pods.

Common Helm labels are currently used only as metadata labels.

## Known security warning

The namespace warns against the Pod Security restricted profile because seccompProfile is not yet set and Postgres uses a root initContainer for volume permissions.

This is a known Phase 3 gap and is not part of the current Helm cleanup.
