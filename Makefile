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
	poetry export --without-hashes --only release-notes > create_release_notes/requirements.txt
	poetry export --without-hashes --only mark-released > mark_jira_released/requirements.txt
	poetry export --without-hashes --only release-cut > release_cut/requirements.txt
	if [ ! -s create_release_notes/requirements.txt ] || [ "$$(grep -v '^[[:space:]]*$$' create_release_notes/requirements.txt | wc -l)" -eq 0 ]; then \
		echo "Error: create_release_notes/requirements.txt is empty or contains only blank lines"; \
		exit 1; \
	fi
	if [ ! -s mark_jira_released/requirements.txt ] || [ "$$(grep -v '^[[:space:]]*$$' mark_jira_released/requirements.txt | wc -l)" -eq 0 ]; then \
		echo "Error: mark_jira_released/requirements.txt is empty or contains only blank lines"; \
		exit 1; \
	fi
	if [ ! -s mark_jira_released/requirements.txt ] || [ "$$(grep -v '^[[:space:]]*$$' mark_jira_released/requirements.txt | wc -l)" -eq 0 ]; then \
		echo "Error: mark_jira_released/requirements.txt is empty or contains only blank lines"; \
		exit 1; \
	fi
	if [ ! -s release_cut/requirements.txt ] || [ "$$(grep -v '^[[:space:]]*$$' release_cut/requirements.txt | wc -l)" -eq 0 ]; then \
		echo "Error: release_cut/requirements.txt is empty or contains only blank lines"; \
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
	poetry export --without-hashes > create_release_notes/requirements.txt
	poetry export --without-hashes --only mark-released > mark_jira_released/requirements.txt
	poetry export --without-hashes --only release-cut > release_cut/requirements.txt
	sam sync \
		--stack-name $$stack_name \
		--watch \
		--template-file SAMtemplates/main_template.yaml

lint-python:
	poetry run black --check create_release_notes
	poetry run flake8 create_release_notes

lint: lint-python cfn-lint


clean:
	rm -rf .aws-sam
	rm -f create_release_notes/requirements.txt

deep-clean: clean
	rm -rf .venv

test:
	poetry run python -m coverage run -m unittest
	poetry run python -m coverage xml

%:
	@$(MAKE) -f /usr/local/share/eps/Mk/common.mk $@
