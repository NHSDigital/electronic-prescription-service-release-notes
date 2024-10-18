# Prescriptions API

![Build](https://github.com/NHSDigital/electronic-prescription-service-release-notes/actions/workflows/release.yml/badge.svg)

This is the code for managing release notes in confluence and releases versions in jira.   
It contains a lambda function to create or update a release notes on confluence for EPS repos. This lambda can also create releases in jira and mark jira tickets with the release version.     
It also has a lambda to mark the release version as released in jira.   
It is intended to be called from github actions as these run outside the UK and access to NHS confluence and jira is geo restricted.   
For descriptions and examples of parameters passed to the lambdas, see the schema in the source code, and the publish* targets in the Makefile

- `create_release_notes/` Lambda code to create the release notes.
- `mark_jira_released/` Lambda code to mark a jira version as released.
- `scripts/` Utilities helpful to developers of this specification.
- `SAMtemplates/` Contains the SAM templates used to define the stack
- `.github` Contains github workflows that are used for building and deploying from pull requests and releases
- `.devcontainer` Contains a dockerfile and vscode devcontainer definition

## Contributing

Contributions to this project are welcome from anyone, providing that they conform to the [guidelines for contribution](https://github.com/NHSDigital/electronic-prescription-service-release-notes/blob/main/CONTRIBUTING.md) and the [community code of conduct](https://github.com/NHSDigital/electronic-prescription-service-release-notes/blob/main/CODE_OF_CONDUCT.md).

### Licensing

This code is dual licensed under the MIT license and the OGL (Open Government License). Any new work added to this repository must conform to the conditions of these licenses. In particular this means that this project may not depend on GPL-licensed or AGPL-licensed libraries, as these would violate the terms of those libraries' licenses.

The contents of this repository are protected by Crown Copyright (C).

## Development

It is recommended that you use visual studio code and a devcontainer as this will install all necessary components and correct versions of tools and languages.  
See https://code.visualstudio.com/docs/devcontainers/containers for details on how to set this up on your host machine.  
The project uses [SAM](https://aws.amazon.com/serverless/sam/) to develop and deploy the APIs and associated resources.

All commits must be made using [signed commits](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits)

Once the steps at the link above have been completed. Add to your ~/.gnupg/gpg.conf as below:

```
use-agent
pinentry-mode loopback
```

and to your ~/.gnupg/gpg-agent.conf as below:

```
allow-loopback-pinentry
```

As described here:
https://stackoverflow.com/a/59170001

You will need to create the files, if they do not already exist.
This will ensure that your VSCode bash terminal prompts you for your GPG key password.

You can cache the gpg key passphrase by following instructions at https://superuser.com/questions/624343/keep-gnupg-credentials-cached-for-entire-user-session

### SAM setup and usage

[SAM](https://aws.amazon.com/serverless/sam/) allows rapid local development and deployment to AWS for development and testing.

### Setup

Ensure you have the following lines in the file .envrc

```
export AWS_DEFAULT_PROFILE=prescription-dev
export stack_name=<UNIQUE_NAME_FOR_YOU>
```

UNIQUE_NAME_FOR_YOU should be a unique name for you with no underscores in it - eg anthony-brown-1

Once you have saved .envrc, start a new terminal in vscode and run this command to authenticate against AWS

```
make aws-configure
```

Put the following values in:

```
SSO session name (Recommended): sso-session
SSO start URL [None]: <USE VALUE OF SSO START URL FROM AWS LOGIN COMMAND LINE ACCESS INSTRUCTIONS ACCESSED FROM https://myapps.microsoft.com>
SSO region [None]: eu-west-2
SSO registration scopes [sso:account:access]:
```

This will then open a browser window and you should authenticate with your hscic credentials
You should then select the development account and set default region to be eu-west-2.

You will now be able to use AWS and SAM CLI commands to access the dev account. You can also use the AWS extension to view resources.

When the token expires, you may need to reauthorise using `make aws-login`

### CI Setup

The GitHub Actions require the following secrets to be added
- AUTOMERGE_PAT. This is a Github personal access token with repo permissions used to auto approve and auto merge dependabot updates
- DEV_CLOUD_FORMATION_DEPLOY_ROLE. This is the cloud formation deploy role ARN in the dev account where the lambda is deployed
- PAT_GITHUB_TOKEN. This is a Github personal access token used by the lambda to avoid rate limits on Github api. It does not need any special permissions
- SONAR_TOKEN. This can be obtained from [SonarCloud](https://sonarcloud.io/) 
as described [here](https://docs.sonarsource.com/sonarqube/latest/user-guide/user-account/generating-and-using-tokens/).
You will need the "Execute Analysis" permission for the project (NHSDigital_electronic-prescription-service-release-notes) in order for the token to work.

### Continuous deployment for testing

You can run the following command to deploy the code to AWS for testing.

```
make sam-sync
```

This will take a few minutes to deploy - you will see something like this when deployment finishes

```
......
CloudFormation events from stack operations (refresh every 0.5 seconds)
---------------------------------------------------------------------------------------------------------------------------------------------------------------------
ResourceStatus                            ResourceType                              LogicalResourceId                         ResourceStatusReason
---------------------------------------------------------------------------------------------------------------------------------------------------------------------
.....
CREATE_COMPLETE                                            AWS::IAM::Policy                                           LambdaExecutionPolicy                                      -                                                        
CREATE_COMPLETE                                            AWS::CloudFormation::Stack                                 rn-ab-1                                                    - 

....

Stack creation succeeded. Sync infra completed.                                                                                                                                                                                             
                                                                                                                                                                                                                                            
Infra sync completed.                
```

Note - the command will keep running and should not be stopped.
You can now call this lamdda from aws console or using aws invoke.


Any code changes you make are automatically uploaded to AWS while `make sam-sync` is running allowing you to quickly test any changes you make

### Pre-commit hooks

Some pre-commit hooks are installed as part of the install above, to run basic lint checks and ensure you can't accidentally commit invalid changes.
The pre-commit hook uses python package pre-commit and is configured in the file .pre-commit-config.yaml.
A combination of these checks are also run in CI.

### Make commands

There are `make` commands that are run as part of the CI pipeline and help alias some functionality during development.

#### install targets

- `install-python` installs python dependencies
- `install-hooks` installs git pre commit hooks
- `install` runs all install targets

#### SAM targets

These are used to do common commands

- `sam-build` prepares the lambdas and SAM definition file to be used in subsequent steps
- `sam-run-local` run the API and lambdas locally
- `sam-sync` sync the API and lambda to AWS. This keeps running and automatically uploads any changes to lambda code made locally. Needs AWS_DEFAULT_PROFILE and stack_name environment variables set.
- `sam-deploy` deploys the compiled SAM template from sam-build to AWS. Needs AWS_DEFAULT_PROFILE and stack_name environment variables set.
- `sam-delete` deletes the deployed SAM cloud formation stack and associated resources. Needs AWS_DEFAULT_PROFILE and stack_name environment variables set.
- `sam-validate` validates the main SAM template and the splunk firehose template.
template.
- `sam-deploy-package` deploys a package created by sam-build. Used in CI builds. Needs the following environment variables set
  - artifact_bucket - bucket where uploaded packaged files are
  - artifact_bucket_prefix - prefix in bucket of where uploaded packaged files ore
  - stack_name - name of stack to deploy
  - template_file - name of template file created by sam-package
  - cloud_formation_execution_role - ARN of role that cloud formation assumes when applying the changeset

#### Clean and deep-clean targets

- `clean` clears up any files that have been generated by building or testing locally.
- `deep-clean` runs clean target and also removes any node_modules and python libraries installed locally.

#### Linting and testing

- `lint` runs lint for all code
- `lint-python` runs lint for python code
- `lint-samtemplates` runs lint for SAM templates
- `test` runs unit tests for all code
- `cfn-guard` runs cfn-guard for sam and cloudformation templates


#### Check licenses

- `check-licenses` checks licenses for all python code

#### CLI Login to AWS

- `aws-configure` configures a connection to AWS
- `aws-login` reconnects to AWS from a previously configured connection

#### Create release notes
By default these all run against the deployed lambdas from the main branch. If you want to run against a lambda from a pull request, you can set the environment variable `pull_request` as `-<pull request id>` - eg
```
export pull_request=-pr-27
```

You must also set environment variables dev_tag, int_tag, prod_tag.

**THE RC RELEASE NOTES CALLS ALSO MODIFY TICKETS IN JIRA BY CHANGING STATUS AND ADDING A FIX SO SHOULD BE USED CAREFULLY**

- `publish-pfp-aws-release-notes-int` Updates release notes for pfp AWS layer showing what is between int_tag and dev_tag
- `publish-pfp-aws-rc-release-notes-int` Creates release notes for pfp AWS layer showing what is between int_tag and dev_tag. Also creates a release in jira and adds fix version to jira tickets found
- `publish-pfp-aws-release-notes-prod` Updates release notes for pfp AWS layer showing what is between prod_tag and dev_tag
- `test-publish-pfp-aws-release-notes-int` Updates test release notes in testing location for pfp AWS layer showing what is between int_tag and dev_tag

- `publish-pfp-apigee-release-notes-int` Updates release notes for pfp Apigee layer showing what is between int_tag and dev_tag
- `publish-pfp-apigee-rc-release-notes-int` Creates release notes for pfp Apigee layer showing what is between int_tag and dev_tag. Also creates a release in jira and adds fix version to jira tickets found
- `publish-pfp-apigee-release-notes-prod` Creates release notes for pfp Apigee layer showing what is between prod_tag and dev_tag
- `test-publish-pfp-apigee-release-notes-int` Updates test release notes in testing location for pfp Apigee layer showing what is between int_tag and dev_tag

- `publish-fhir-release-notes-int` Updates release notes for FHIR api showing what is between int_tag and dev_tag
- `publish-fhir-rc-release-notes-int` Creates release notes for FHIR api showing what is between int_tag and dev_tag. Also creates a release in jira and adds fix version to jira tickets found
- `publish-fhir-release-notes-prod` Creates release notes for FHIR api showing what is between prod_tag and dev_tag
- `publish-fhir-release-notes-int` Updates test release notes in testing location for FHIR api showing what is between int_tag and dev_tag

- `publish-account-resources-release-notes-int` Updates release notes for FHIR api showing what is between int_tag and dev_tag
- `publish-account-resources-rc-release-notes-int` Creates release notes for FHIR api showing what is between int_tag and dev_tag. Also creates a release in jira and adds fix version to jira tickets found
- `publish-account-resources-release-notes-prod` Creates release notes for FHIR api showing what is between prod_tag and dev_tag
- `publish-account-resources-release-notes-int` Updates test release notes in testing location for FHIR api showing what is between int_tag and dev_tag

- `mark-jira-released` Marks a jira version as released

### Github folder

This .github folder contains workflows and templates related to github

- `pull_request_template.yml`: Template for pull requests.

Workflows are in the .github/workflows folder

- `combine-dependabot-prs.yml`: Workflow for combining dependabot pull requests. Runs on demand
- `delete_old_cloudformation_stacks.yml`: Workflow for deleting old cloud formation stacks. Runs daily
- `pull_request.yml`: Called when pull request is opened or updated. Calls sam_package_code and sam_release_code to build and deploy the code. Deploys to dev AWS account. The stack has name release-notes-pr-<PULL_REQUEST_ID> in the name
- `release.yml`: Run when code is merged to main branch or a tag starting v is pushed. Calls sam_package_code and sam_release_code to build and deploy the code.
- `sam_package_code.yml`: Packages code and uploads to a github artifact for later deployment
- `sam_release_code.yml`: Release code built by sam_package_code.yml to an environment
- `pr-link.yaml`: This workflow template links Pull Requests to Jira tickets and runs when a pull request is opened.
- `dependabot_auto_approve_and_merge.yml`: Automatically approves and merges dependabot changes
- `dependabot.yml`: Dependabot definition file
