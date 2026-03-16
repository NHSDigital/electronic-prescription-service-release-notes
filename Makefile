.PHONY: install-python install-hooks build install mark-jira-released sam-build sam-run-local sam-deploy-package sam-validate sam-sync lint-python lint clean deep-clean test install-node
guard-%:
	@ if [ "${${*}}" = "" ]; then \
		echo "Environment variable $* not set"; \
		exit 1; \
	fi

install-python:
	poetry install

install-hooks: install-python
	poetry run pre-commit install --install-hooks --overwrite

install-node:
	npm ci

build:
	echo "Does nothing"

install: install-python install-hooks install-node

mark-jira-released: guard-release_version
	echo { \"releaseVersion\": \"$$release_version\" } > /tmp/payload.json
	aws lambda invoke \
		--function-name "release-notes$${pull_request}-markJiraReleased" \
		--cli-binary-format raw-in-base64-out \
		--payload file:///tmp/payload.json /tmp/out.txt
	cat /tmp/out.txt


lint-python:
	poetry run black --check packages
	poetry run flake8 packages

lint-node:
	npm run lint --workspace packages/cdk
lint: lint-node lint-python cfn-lint

compile:
	echo "Does nothing"
clean:
	rm -rf .aws-sam
	rm -f packages/create_release_notes/app/requirements.txt
	rm -f packages/mark_jira_released/app/requirements.txt
	rm -f packages/release_cut/app/requirements.txt

deep-clean: clean
	rm -rf .venv
	find . -name 'node_modules' -type d -prune -exec rm -rf '{}' +

test:
	PYTHONPATH=packages/create_release_notes/app:packages/mark_jira_released/app:packages/release_cut/app:. poetry run python -m coverage run -m unittest discover -s packages/create_release_notes/test -p "test_*.py"
	PYTHONPATH=packages/create_release_notes/app:packages/mark_jira_released/app:packages/release_cut/app:. poetry run python -m coverage run --append -m unittest discover -s packages/mark_jira_released/test -p "test_*.py"
	PYTHONPATH=packages/create_release_notes/app:packages/mark_jira_released/app:packages/release_cut/app:. poetry run python -m coverage run --append -m unittest discover -s packages/release_cut/test -p "test_*.py"
	poetry run python -m coverage xml

cdk-synth:
	mkdir -p .dependencies/create_release_notes
	mkdir -p .dependencies/mark_jira_released
	mkdir -p .dependencies/release_cut
	CDK_APP_NAME=ReleaseNotesApp \
	CDK_CONFIG_versionNumber=undefined \
	CDK_CONFIG_commitId=undefined \
	CDK_CONFIG_isPullRequest=false \
	CDK_CONFIG_environment=dev \
	CDK_CONFIG_LOG_RETENTION_IN_DAYS=30 \
	CDK_CONFIG_stackName=ReleaseNotes \
	npm run cdk-synth --workspace packages/cdk/
	
create-npmrc:
	gh auth login --scopes "read:packages"; \
	echo "//npm.pkg.github.com/:_authToken=$$(gh auth token)" > .npmrc
	echo "@nhsdigital:registry=https://npm.pkg.github.com" >> .npmrc
%:
	@$(MAKE) -f /usr/local/share/eps/Mk/common.mk $@
