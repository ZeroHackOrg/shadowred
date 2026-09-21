{{- define "shadowred.name" -}}
{{ default .Chart.Name .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end -}}

{{- define "shadowred.fullname" -}}
{{ .Release.Name | printf "%s-shadowred" | trunc 63 | trimSuffix "-" }}
{{- end -}}