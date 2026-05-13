SHELL := /bin/bash
.RECIPEPREFIX := >

RELEASE ?= devops-platform
NAMESPACE ?= devops-lab
CHART ?= charts/devops-platform
VALUES ?= $(CHART)/values-dev.yaml
RENDERED ?= /tmp/$(RELEASE)-rendered.yaml

.PHONY: helm-lint helm-render helm-diff helm-upgrade helm-status helm-history app-verify helm-check helm-release

helm-lint:
> helm lint $(CHART) -f $(VALUES)

helm-render:
> helm template $(RELEASE) $(CHART) -n $(NAMESPACE) -f $(VALUES) > $(RENDERED)
> echo "Rendered to $(RENDERED)"

helm-diff: helm-render
> kubectl diff -n $(NAMESPACE) -f $(RENDERED)

helm-upgrade:
> helm upgrade $(RELEASE) $(CHART) -n $(NAMESPACE) -f $(VALUES) --atomic --timeout 5m

helm-status:
> helm status $(RELEASE) -n $(NAMESPACE)

helm-history:
> helm history $(RELEASE) -n $(NAMESPACE)

app-verify:
> curl -s -o /dev/null -w "frontend: %{http_code}\n" http://app.local/
> curl -s -o /dev/null -w "api: %{http_code}\n" http://app.local/api
> curl -s -o /dev/null -w "db: %{http_code}\n" http://app.local/api/db

helm-check: helm-lint helm-diff

helm-release: helm-check helm-upgrade helm-status app-verify
