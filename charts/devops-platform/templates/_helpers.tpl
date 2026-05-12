{{/*
Chart name.
*/}}
{{- define "devops-platform.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Release-aware full name.
*/}}
{{- define "devops-platform.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s" .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Standard Kubernetes/Helm labels.
These labels describe ownership and chart metadata.
They are safe for metadata.labels, but should NOT all be used as selectors.
*/}}
{{- define "devops-platform.labels" -}}
app.kubernetes.io/name: {{ include "devops-platform.name" . | quote }}
app.kubernetes.io/instance: {{ .Release.Name | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service | quote }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | quote }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
{{- end }}

{{/*
Stable selector labels.
Only stable labels should be used in spec.selector and pod template labels.
Do not include chart version here, because selector fields are immutable.
*/}}
{{- define "devops-platform.selectorLabels" -}}
app.kubernetes.io/name: {{ include "devops-platform.name" . | quote }}
app.kubernetes.io/instance: {{ .Release.Name | quote }}
{{- end }}

{{/*
Component-specific metadata labels.
Usage example:
{{ include "devops-platform.componentLabels" (dict "root" . "component" "backend") }}
*/}}
{{- define "devops-platform.componentLabels" -}}
{{ include "devops-platform.labels" .root }}
app.kubernetes.io/component: {{ .component | quote }}
{{- end }}

{{/*
Component-specific selector labels.
Usage example:
{{ include "devops-platform.componentSelectorLabels" (dict "root" . "component" "backend") }}
*/}}
{{- define "devops-platform.componentSelectorLabels" -}}
{{ include "devops-platform.selectorLabels" .root }}
app.kubernetes.io/component: {{ .component | quote }}
{{- end }}
