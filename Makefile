guard-%:
	@ if [ "${${*}}" = "" ]; then \
		echo "Environment variable $* not set"; \
		exit 1; \
	fi

install-python:
	poetry install

install-hooks: install-python
	poetry run pre-commit install --install-hooks --overwrite

install: install-python install-hooks

publish-pfp-aws-release-notes-int:
	dev_tag=$$(aws cloudformation describe-stacks --stack-name dev-ci --profile prescription-dev --query "Stacks[0].Tags[?Key=='version'].Value" --output text); \
	int_tag=$$(aws cloudformation describe-stacks --stack-name int-ci --profile prescription-int --query "Stacks[0].Tags[?Key=='version'].Value" --output text); \
	echo { \"currentTag\": \"$$int_tag\", \"targetTag\": \"$$dev_tag\", \"repoName\": \"prescriptionsforpatients\", \"targetEnvironment\": \"INT\", \"productName\": \"Prescriptions for Patients AWS layer\", \"releaseNotesPageId\": \"734733361\", \"releaseNotesPageTitle\": \"Current PfP AWS layer release notes - INT\" } > /tmp/payload.json
	aws lambda invoke \
		--function-name "release-notes$${pull_request}-createReleaseNotes" \
		--cli-binary-format raw-in-base64-out \
		--payload file:///tmp/payload.json /tmp/out.txt
	cat /tmp/out.txt

test-publish-pfp-aws-release-notes-int:
	dev_tag=$$(aws cloudformation describe-stacks --stack-name dev-ci --profile prescription-dev --query "Stacks[0].Tags[?Key=='version'].Value" --output text); \
	int_tag=$$(aws cloudformation describe-stacks --stack-name int-ci --profile prescription-int --query "Stacks[0].Tags[?Key=='version'].Value" --output text); \
	echo { \"currentTag\": \"$$int_tag\", \"targetTag\": \"$$dev_tag\", \"repoName\": \"prescriptionsforpatients\", \"targetEnvironment\": \"INT\", \"productName\": \"Prescriptions for Patients AWS layer\", \"releaseNotesPageId\": \"768063755\", \"releaseNotesPageTitle\": \"Current PfP AWS layer release notes - TESTING\" } > /tmp/payload.json
	aws lambda invoke \
		--function-name "release-notes$${pull_request}-createReleaseNotes" \
		--cli-binary-format raw-in-base64-out \
		--payload file:///tmp/payload.json /tmp/out.txt
	cat /tmp/out.txt

publish-pfp-aws-rc-release-notes-int:
	dev_tag=$$(aws cloudformation describe-stacks --stack-name dev-ci --profile prescription-dev --query "Stacks[0].Tags[?Key=='version'].Value" --output text); \
	int_tag=$$(aws cloudformation describe-stacks --stack-name int-ci --profile prescription-int --query "Stacks[0].Tags[?Key=='version'].Value" --output text); \
	echo { \"createReleaseCandidate\": \"true\", \"releasePrefix\": \"PfP-AWS-\", \"currentTag\": \"$$int_tag\", \"targetTag\": \"$$dev_tag\", \"repoName\": \"prescriptionsforpatients\", \"targetEnvironment\": \"INT\", \"productName\": \"Prescriptions for Patients AWS layer\", \"releaseNotesPageId\": \"734733361\", \"releaseNotesPageTitle\": \"WITHOUT RUN LINK PfP-AWS-$$dev_tag - Deployed to [INT] on $$(date +'%d-%m-%y')\"} > /tmp/payload.json
	aws lambda invoke \
		--function-name "release-notes$${pull_request}-createReleaseNotes" \
		--cli-binary-format raw-in-base64-out \
		--payload file:///tmp/payload.json /tmp/out.txt
	cat /tmp/out.txt

publish-pfp-aws-release-notes-prod:
	dev_tag=$$(aws cloudformation describe-stacks --stack-name dev-ci --profile prescription-dev --query "Stacks[0].Tags[?Key=='version'].Value" --output text); \
	prod_tag=$$(aws cloudformation describe-stacks --stack-name prod-ci --profile prescription-prod --query "Stacks[0].Tags[?Key=='version'].Value" --output text); \
	echo { \"currentTag\": \"$$prod_tag\", \"targetTag\": \"$$dev_tag\", \"repoName\": \"prescriptionsforpatients\", \"targetEnvironment\": \"PROD\", \"productName\": \"Prescriptions for Patients AWS layer\", \"releaseNotesPageId\": \"693750029\", \"releaseNotesPageTitle\": \"Current PfP AWS layer release notes - PROD\" } > /tmp/payload.json
	aws lambda invoke \
		--function-name "release-notes$${pull_request}-createReleaseNotes" \
		--cli-binary-format raw-in-base64-out \
		--payload file:///tmp/payload.json /tmp/out.txt
	cat /tmp/out.txt

publish-pfp-apigee-release-notes-int:
	dev_tag=$$(curl -s "https://internal-dev.api.service.nhs.uk/prescriptions-for-patients/_ping" | jq --raw-output ".version"); \
	int_tag=$$(curl -s "https://int.api.service.nhs.uk/prescriptions-for-patients/_ping" | jq --raw-output ".version"); \
	echo { \"currentTag\": \"$$int_tag\", \"targetTag\": \"$$dev_tag\", \"repoName\": \"prescriptions-for-patients\", \"targetEnvironment\": \"INT\", \"productName\": \"Prescriptions for Patients Apigee layer\", \"releaseNotesPageId\": \"693750035\", \"releaseNotesPageTitle\": \"Current PfP Apigee layer release notes - INT\" } > /tmp/payload.json
	aws lambda invoke \
		--function-name "release-notes$${pull_request}-createReleaseNotes" \
		--cli-binary-format raw-in-base64-out \
		--payload file:///tmp/payload.json /tmp/out.txt
	cat /tmp/out.txt

test-publish-pfp-apigee-release-notes-int:
	dev_tag=$$(curl -s "https://internal-dev.api.service.nhs.uk/prescriptions-for-patients/_ping" | jq --raw-output ".version"); \
	int_tag=$$(curl -s "https://int.api.service.nhs.uk/prescriptions-for-patients/_ping" | jq --raw-output ".version"); \
	echo { \"currentTag\": \"$$int_tag\", \"targetTag\": \"$$dev_tag\", \"repoName\": \"prescriptions-for-patients\", \"targetEnvironment\": \"INT\", \"productName\": \"Prescriptions for Patients Apigee layer\", \"releaseNotesPageId\": \"768063758\", \"releaseNotesPageTitle\": \"Current PfP Apigee layer release notes - TESTING\" } > /tmp/payload.json
	aws lambda invoke \
		--function-name "release-notes$${pull_request}-createReleaseNotes" \
		--cli-binary-format raw-in-base64-out \
		--payload file:///tmp/payload.json /tmp/out.txt
	cat /tmp/out.txt

publish-pfp-apigee-rc-release-notes-int:
	dev_tag=$$(curl -s "https://internal-dev.api.service.nhs.uk/prescriptions-for-patients/_ping" | jq --raw-output ".version"); \
	int_tag=$$(curl -s "https://int.api.service.nhs.uk/prescriptions-for-patients/_ping" | jq --raw-output ".version"); \
	echo { \"createReleaseCandidate\": \"true\", \"releasePrefix\": \"PfP-Apigee-\", \"currentTag\": \"$$int_tag\", \"targetTag\": \"$$dev_tag\", \"repoName\": \"prescriptions-for-patients\", \"targetEnvironment\": \"INT\", \"productName\": \"Prescriptions for Patients Apigee layer\", \"releaseNotesPageId\": \"710051478\", \"releaseNotesPageTitle\": \"PfP-APigee-$$dev_tag - Deployed to [INT] on $$(date +'%d-%m-%y')\" } > /tmp/payload.json
	aws lambda invoke \
		--function-name "release-notes$${pull_request}-createReleaseNotes" \
		--cli-binary-format raw-in-base64-out \
		--payload file:///tmp/payload.json /tmp/out.txt
	cat /tmp/out.txt

publish-pfp-apigee-release-notes-prod:
	dev_tag=$$(curl -s "https://internal-dev.api.service.nhs.uk/prescriptions-for-patients/_ping" | jq --raw-output ".version"); \
	prod_tag=$$(curl -s "https://api.service.nhs.uk/prescriptions-for-patients/_ping" | jq --raw-output ".version"); \
	echo { \"currentTag\": \"$$prod_tag\", \"targetTag\": \"$$dev_tag\", \"repoName\": \"prescriptions-for-patients\", \"targetEnvironment\": \"PROD\", \"productName\": \"Prescriptions for Patients Apigee layer\", \"releaseNotesPageId\": \"693750032\", \"releaseNotesPageTitle\": \"Current PfP Apigee layer release notes - PROD\" } > /tmp/payload.json
	aws lambda invoke \
		--function-name "release-notes$${pull_request}-createReleaseNotes" \
		--cli-binary-format raw-in-base64-out \
		--payload file:///tmp/payload.json /tmp/out.txt
	cat /tmp/out.txt

publish-fhir-release-notes-int:
	dev_tag=$$(curl -s "https://internal-dev.api.service.nhs.uk/electronic-prescriptions/_ping" | jq --raw-output ".version"); \
	int_tag=$$(curl -s "https://int.api.service.nhs.uk/electronic-prescriptions/_ping" | jq --raw-output ".version"); \
	echo { \"currentTag\": \"$$int_tag\", \"targetTag\": \"$$dev_tag\", \"repoName\": \"electronic-prescription-service-api\", \"targetEnvironment\": \"INT\", \"productName\": \"FHIR API\", \"releaseNotesPageId\": \"587367089\", \"releaseNotesPageTitle\": \"Current FHIR API release notes - INT\" } > /tmp/payload.json
	aws lambda invoke \
		--function-name "release-notes$${pull_request}-createReleaseNotes" \
		--cli-binary-format raw-in-base64-out \
		--payload file:///tmp/payload.json /tmp/out.txt
	cat /tmp/out.txt

test-publish-fhir-release-notes-int:
	dev_tag=$$(curl -s "https://internal-dev.api.service.nhs.uk/electronic-prescriptions/_ping" | jq --raw-output ".version"); \
	int_tag=$$(curl -s "https://int.api.service.nhs.uk/electronic-prescriptions/_ping" | jq --raw-output ".version"); \
	echo { \"currentTag\": \"$$int_tag\", \"targetTag\": \"$$dev_tag\", \"repoName\": \"electronic-prescription-service-api\", \"targetEnvironment\": \"INT\", \"productName\": \"FHIR API\", \"releaseNotesPageId\": \"734403724\", \"releaseNotesPageTitle\": \"Current FHIR API release notes - TESTING\" } > /tmp/payload.json
	aws lambda invoke \
		--function-name "release-notes$${pull_request}-createReleaseNotes" \
		--cli-binary-format raw-in-base64-out \
		--payload file:///tmp/payload.json /tmp/out.txt
	cat /tmp/out.txt

publish-fhir-rc-release-notes-int:
	dev_tag=$$(curl -s "https://internal-dev.api.service.nhs.uk/electronic-prescriptions/_ping" | jq --raw-output ".version"); \
	int_tag=$$(curl -s "https://int.api.service.nhs.uk/electronic-prescriptions/_ping" | jq --raw-output ".version"); \
	echo { \"createReleaseCandidate\": \"true\", \"releasePrefix\": \"FHIR-\", \"currentTag\": \"$$int_tag\", \"targetTag\": \"$$dev_tag\", \"repoName\": \"electronic-prescription-service-api\", \"targetEnvironment\": \"INT\", \"productName\": \"FHIR API\", \"releaseNotesPageId\": \"587372008\", \"releaseNotesPageTitle\": \"FHIR-$$dev_tag - Deployed to [INT] on $$(date +'%d-%m-%y')\" } > /tmp/payload.json
	aws lambda invoke \
		--function-name "release-notes$${pull_request}-createReleaseNotes" \
		--cli-binary-format raw-in-base64-out \
		--payload file:///tmp/payload.json /tmp/out.txt
	cat /tmp/out.txt

publish-fhir-release-notes-prod:
	dev_tag=$$(curl -s "https://internal-dev.api.service.nhs.uk/electronic-prescriptions/_ping" | jq --raw-output ".version"); \
	prod_tag=$$(curl -s "https://api.service.nhs.uk/electronic-prescriptions/_ping" | jq --raw-output ".version"); \
	echo { \"currentTag\": \"$$prod_tag\", \"targetTag\": \"$$dev_tag\", \"repoName\": \"electronic-prescription-service-api\", \"targetEnvironment\": \"PROD\", \"productName\": \"FHIR API\", \"releaseNotesPageId\": \"587367100\", \"releaseNotesPageTitle\": \"Current FHIR API release notes - PROD\" } > /tmp/payload.json
	aws lambda invoke \
		--function-name "release-notes$${pull_request}-createReleaseNotes" \
		--cli-binary-format raw-in-base64-out \
		--payload file:///tmp/payload.json /tmp/out.txt
	cat /tmp/out.txt

publish-account-resources-release-notes-int:
	dev_tag=$$(curl -s "https://internal-dev.api.service.nhs.uk/electronic-prescriptions/_ping" | jq --raw-output ".version"); \
	int_tag=$$(curl -s "https://int.api.service.nhs.uk/electronic-prescriptions/_ping" | jq --raw-output ".version"); \
	echo { \"currentTag\": \"$$int_tag\", \"targetTag\": \"$$dev_tag\", \"repoName\": \"electronic-prescription-service-account-resources\", \"targetEnvironment\": \"INT\", \"productName\": \"AWS account resources\", \"releaseNotesPageId\": \"749733665\", \"releaseNotesPageTitle\": \"Current AWS account resources release notes - INT\" } > /tmp/payload.json
	aws lambda invoke \
		--function-name "release-notes$${pull_request}-createReleaseNotes" \
		--cli-binary-format raw-in-base64-out \
		--payload file:///tmp/payload.json /tmp/out.txt
	cat /tmp/out.txt

test-publish-account-resources-release-notes-int:
	dev_tag=$$(curl -s "https://internal-dev.api.service.nhs.uk/electronic-prescriptions/_ping" | jq --raw-output ".version"); \
	int_tag=$$(curl -s "https://int.api.service.nhs.uk/electronic-prescriptions/_ping" | jq --raw-output ".version"); \
	echo { \"currentTag\": \"$$int_tag\", \"targetTag\": \"$$dev_tag\", \"repoName\": \"electronic-prescription-service-account-resources\", \"targetEnvironment\": \"INT\", \"productName\": \"AWS account resources\", \"releaseNotesPageId\": \"768063770\", \"releaseNotesPageTitle\": \"Current AWS account resources release notes - TESTING\" } > /tmp/payload.json
	aws lambda invoke \
		--function-name "release-notes$${pull_request}-createReleaseNotes" \
		--cli-binary-format raw-in-base64-out \
		--payload file:///tmp/payload.json /tmp/out.txt
	cat /tmp/out.txt

publish-account-resources-rc-release-notes-int:
	dev_tag=$$(curl -s "https://internal-dev.api.service.nhs.uk/electronic-prescriptions/_ping" | jq --raw-output ".version"); \
	int_tag=$$(curl -s "https://int.api.service.nhs.uk/electronic-prescriptions/_ping" | jq --raw-output ".version"); \
	echo { \"createReleaseCandidate\": \"true\", \"releasePrefix\": \"AWS-account-resources-\", \"currentTag\": \"$$int_tag\", \"targetTag\": \"$$dev_tag\", \"repoName\": \"electronic-prescription-service-account-resources\", \"targetEnvironment\": \"INT\", \"productName\": \"AWS account resources\", \"releaseNotesPageId\": \"749733675\", \"releaseNotesPageTitle\": \"FHIR-$$dev_tag - Deployed to [INT] on $$(date +'%d-%m-%y')\" } > /tmp/payload.json
	aws lambda invoke \
		--function-name "release-notes$${pull_request}-createReleaseNotes" \
		--cli-binary-format raw-in-base64-out \
		--payload file:///tmp/payload.json /tmp/out.txt
	cat /tmp/out.txt

publish-account-resources-release-notes-prod:
	dev_tag=$$(curl -s "https://internal-dev.api.service.nhs.uk/electronic-prescriptions/_ping" | jq --raw-output ".version"); \
	prod_tag=$$(curl -s "https://api.service.nhs.uk/electronic-prescriptions/_ping" | jq --raw-output ".version"); \
	echo { \"currentTag\": \"$$prod_tag\", \"targetTag\": \"$$dev_tag\", \"repoName\": \"electronic-prescription-service-account-resources\", \"targetEnvironment\": \"PROD\", \"productName\": \"AWS account resources\", \"releaseNotesPageId\": \"749733670\", \"releaseNotesPageTitle\": \"Current FHIR API release notes - PROD\" } > /tmp/payload.json
	aws lambda invoke \
		--function-name "release-notes$${pull_request}-createReleaseNotes" \
		--cli-binary-format raw-in-base64-out \
		--payload file:///tmp/payload.json /tmp/out.txt
	cat /tmp/out.txt

mark-jira-released: guard-release_version
	echo { \"releaseVersion\": \"$$release_version\" } > /tmp/payload.json
	aws lambda invoke \
		--function-name "release-notes$${pull_request}-markJiraReleased" \
		--cli-binary-format raw-in-base64-out \
		--payload file:///tmp/payload.json /tmp/out.txt
	cat /tmp/out.txt

aws-login:
	aws sso login --sso-session sso-session

aws-configure:
	aws configure sso --region eu-west-2

sam-build: sam-validate
	poetry export --without-hashes --only release_notes > create_release_notes/requirements.txt
	poetry export --without-hashes --only mark_released > mark_jira_released/requirements.txt
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
	sam sync \
		--stack-name $$stack_name \
		--watch \
		--template-file SAMtemplates/main_template.yaml

sam-delete: guard-AWS_DEFAULT_PROFILE guard-stack_name
	sam delete --stack-name $$stack_name

lint-samtemplates:
	poetry run cfn-lint -t SAMtemplates/*.yaml

lint-python:
	poetry run black --check create_release_notes
	poetry run flake8 create_release_notes

lint: lint-python lint-samtemplates

check-licenses:
	scripts/check_python_licenses.sh

clean:
	rm -rf .aws-sam
	rm create_release_notes/requirements.txt

deep-clean: clean
	rm -rf .venv

test:
	poetry run python -m coverage run -m unittest
	poetry run python -m coverage xml
