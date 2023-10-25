# Prescriptions API

![Build](https://github.com/NHSDigital/electronic-prescription-service-release-notes/workflows/release/badge.svg?branch=main)

This is the code for a lambda function to create release notes on confluence for electronic prescription service code. It is intended to be called from github actions as these run outside the UK and access to NHS confluence and jira is geo restricted

- `packages/create_release_notes/` Lambda code to create the release notes.
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

The GitHub Actions require a secret to exist on the repo called "SONAR_TOKEN".
This can be obtained from [SonarCloud](https://sonarcloud.io/)
as described [here](https://docs.sonarsource.com/sonarqube/latest/user-guide/user-account/generating-and-using-tokens/).
You will need the "Execute Analysis" permission for the project (NHSDigital_electronic-prescription-service-release-notes) in order for the token to work.

### Continuous deployment for testing

You can run the following command to deploy the code to AWS for testing. Once deployed you will need to set the secrets confluence token and jira token to valid tokens. See https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html on how to create these

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


#### Check licenses

- `check-licenses` checks licenses for all python code

#### CLI Login to AWS

- `aws-configure` configures a connection to AWS
- `aws-login` reconnects to AWS from a previously configured connection

### Github folder

This .github folder contains workflows and templates related to github

- `pull_request_template.yml`: Template for pull requests.

Workflows are in the .github/workflows folder

- `combine-dependabot-prs.yml`: Workflow for combining dependabot pull requests. Runs on demand
- `delete_old_cloudformation_stacks.yml`: Workflow for deleting old cloud formation stacks. Runs daily
- `pull_request.yml`: Called when pull request is opened or updated. Calls sam_package_code and sam_release_code to build and deploy the code. Deploys to dev AWS account. The main and sandbox stacks deployed have PR-<PULL_REQUEST_ID> in the name
- `quality_checks.yml`: Runs check-licenses, lint, test and sonarcloud scan against the repo. Called from pull_request.yml and release.yml
- `release.yml`: Run when code is merged to main branch or a tag starting v is pushed. Calls sam_package_code and sam_release_code to build and deploy the code.
- `sam_package_code.yml`: Packages code and uploads to a github artifact for later deployment
- `sam_release_code.yml`: Release code built by sam_package_code.yml to an environment
- `pr-link.yaml`: This workflow template links Pull Requests to Jira tickets and runs when a pull request is opened.
- `dependabot.yml`: Dependabot definition file
