{{/*
Expand the name of the chart.
*/}}
{{- define "todolist.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "todolist.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "todolist.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todolist.labels" -}}
helm.sh/chart: {{ include "todolist.chart" . }}
{{ include "todolist.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todolist.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todolist.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "todolist.frontend.labels" -}}
{{ include "todolist.labels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Frontend selector labels
*/}}
{{- define "todolist.frontend.selectorLabels" -}}
{{ include "todolist.selectorLabels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Backend labels
*/}}
{{- define "todolist.backend.labels" -}}
{{ include "todolist.labels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Backend selector labels
*/}}
{{- define "todolist.backend.selectorLabels" -}}
{{ include "todolist.selectorLabels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
ConfigMap name
*/}}
{{- define "todolist.configMapName" -}}
{{ include "todolist.fullname" . }}-config
{{- end }}

{{/*
Secret name
*/}}
{{- define "todolist.secretName" -}}
{{ include "todolist.fullname" . }}-secrets
{{- end }}
