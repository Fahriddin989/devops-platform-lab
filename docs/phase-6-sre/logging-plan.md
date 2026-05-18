# Phase 6.2 — Centralized Logging

## Goal

Move from per-Pod `kubectl logs` to centralized searchable logs.

## Architecture

Pod stdout/stderr
-> Grafana Alloy
-> Loki
-> Grafana / LogQL

## Placement

Logging is a platform observability layer.

It does not belong inside:

- charts/devops-platform

It belongs under:

- platform/logging
- gitops/argocd/platform-logging-application.yaml

## Initial implementation

- Loki: single-binary mode for lab
- Alloy: Kubernetes pod log collector
- Grafana UI: added after logs are flowing

## Production notes

For real production:

- use object storage such as S3
- define retention
- set resource requests/limits
- avoid logging secrets
- use structured JSON logs
- use request_id for correlation
