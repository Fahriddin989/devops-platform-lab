# Phase 6 — Storage Foundation

## Why this was needed

Loki requires persistent storage because logs should survive Pod restarts.

The initial Loki PVC stayed Pending because the EKS cluster did not have the Amazon EBS CSI driver installed.

## Fix

Installed Amazon EBS CSI driver as an EKS managed add-on.

## Result

Kubernetes can dynamically provision EBS volumes for PersistentVolumeClaims.

Verified:

- ebs-csi-controller Running
- ebs-csi-node Running on both nodes
- CSIDriver ebs.csi.aws.com exists
- Loki PVC storage-loki-0 Bound
- Loki Pod Running

## Production note

EBS CSI is a cluster-level storage capability.

It does not belong inside the application Helm chart.
