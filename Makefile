.PHONY: install-python install-hooks build install mark-jira-released sam-build sam-run-local sam-deploy-package sam-validate sam-sync lint-python lint clean deep-clean test
guard-%:
	@ if [ "${${*}}" = "" ]; then \
		echo "Environment variable $* not set"; \
		exit 1; \
	fi

install-python:
	poetry install

install-hooks: install-python
	poetry run pre-commit install --install-hooks --overwrite

build:
	echo "Does nothing"

install: install-python install-hooks

mark-jira-released: guard-release_version
	echo { \"releaseVersion\": \"$$release_version\" } > /tmp/payload.json
	aws lambda invoke \
		--function-name "release-notes$${pull_request}-markJiraReleased" \
		--cli-binary-format raw-in-base64-out \
		--payload file:///tmp/payload.json /tmp/out.txt
	cat /tmp/out.txt


sam-build: sam-validate
	poetry export --without-hashes --only release-notes > packages/create_release_notes/app/requirements.txt
	poetry export --without-hashes --only mark-released > packages/mark_jira_release/app/requirements.txt
	poetry export --without-hashes --only release-cut > packages/release_cut/app/requirements.txt
	if [ ! -s packages/create_release_notes/app/requirements.txt ] || [ "$$(grep -v '^[[:space:]]*$$' packages/create_release_notes/app/requirements.txt | wc -l)" -eq 0 ]; then \
		echo "Error: packages/create_release_notes/app/requirements.txt is empty or contains only blank lines"; \
		exit 1; \
	fi
	if [ ! -s packages/mark_jira_release/app/requirements.txt ] || [ "$$(grep -v '^[[:space:]]*$$' packages/mark_jira_release/app/requirements.txt | wc -l)" -eq 0 ]; then \
		echo "Error: packages/mark_jira_release/app/requirements.txt is empty or contains only blank lines"; \
		exit 1; \
	fi
	if [ ! -s packages/release_cut/app/requirements.txt ] || [ "$$(grep -v '^[[:space:]]*$$' packages/release_cut/app/requirements.txt | wc -l)" -eq 0 ]; then \
		echo "Error: packages/release_cut/app/requirements.txt is empty or contains only blank lines"; \
		exit 1; \
	fi
	sam build --template-file SAMtemplates/main_template.yaml --region eu-west-2

sam-run-local: sam-build
	sam local start-lambda

sam-deploy-package: guard-artifact_bucket guard-artifact_bucket_prefix guard-stack_name guard-template_file guard-cloud_formation_execution_role
	sam deploy \
		--template-file $$template_file \
		--stack-name $$stack_name \
		--capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
		--region eu-west-2 \
		--s3-bucket $$artifact_bucket \
		--s3-prefix $$artifact_bucket_prefix \
		--config-file samconfig_package_and_deploy.toml \
		--no-fail-on-empty-changeset \
		--role-arn $$cloud_formation_execution_role \
		--no-confirm-changeset \
		--force-upload \
		--tags "version=$$VERSION_NUMBER" \
		--parameter-overrides \
			GithubToken=$$PAT_GITHUB_TOKEN


sam-validate: 
	sam validate --template-file SAMtemplates/main_template.yaml --region eu-west-2

sam-sync: guard-AWS_DEFAULT_PROFILE guard-stack_name
	poetry export --without-hashes > packages/create_release_notes/app/requirements.txt
	poetry export --without-hashes --only mark-released > packages/mark_jira_release/app/requirements.txt
	poetry export --without-hashes --only release-cut > packages/release_cut/app/requirements.txt
	sam sync \
		--stack-name $$stack_name \
		--watch \
		--template-file SAMtemplates/main_template.yaml

lint-python:
	poetry run black --check packages
	poetry run flake8 packages

lint: lint-python cfn-lint


clean:
	rm -rf .aws-sam
	rm -f packages/create_release_notes/app/requirements.txt
	rm -f packages/mark_jira_release/app/requirements.txt
	rm -f packages/release_cut/app/requirements.txt

deep-clean: clean
	rm -rf .venv

test:
	PYTHONPATH=packages/create_release_notes/app:packages/mark_jira_release/app:packages/release_cut/app:. poetry run python -m coverage run -m unittest discover -s packages/create_release_notes/test -p "test_*.py"
	PYTHONPATH=packages/create_release_notes/app:packages/mark_jira_release/app:packages/release_cut/app:. poetry run python -m coverage run --append -m unittest discover -s packages/mark_jira_release/test -p "test_*.py"
	PYTHONPATH=packages/create_release_notes/app:packages/mark_jira_release/app:packages/release_cut/app:. poetry run python -m coverage run --append -m unittest discover -s packages/release_cut/test -p "test_*.py"
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
