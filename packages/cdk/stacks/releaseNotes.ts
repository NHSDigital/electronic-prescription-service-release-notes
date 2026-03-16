import {
  App,
  Fn,
  Stack,
  StackProps,
} from "aws-cdk-lib"
import { Functions } from "../resources/Functions"
import { Policies } from "../resources/Policies"
import { Role } from "aws-cdk-lib/aws-iam"
import { Secret } from "aws-cdk-lib/aws-secretsmanager"

import {nagSuppressions} from "../nagSuppressions"

export interface ReleaseNotesProps extends StackProps {
  readonly stackName: string
  readonly version: string
  readonly commitId: string
  readonly isPullRequest: boolean
}

export class ReleaseNotes extends Stack {
  public constructor(scope: App, id: string, props: ReleaseNotesProps) {
    super(scope, id, props)

    const deploymentRoleImport = Fn.importValue("ci-resources:CloudFormationDeployRole")
    const releaseNotesExecuteLambdaRoleImport = Fn.importValue("ci-resources:ReleaseNotesExecuteLambdaRole")
    const jiraTokenSecretImport = Fn.importValue("account-resources:JiraToken")
    const confluenceTokenSecretImport = Fn.importValue("account-resources:ConfluenceToken")

    const deploymentRole = Role.fromRoleArn(this, "deploymentRole", deploymentRoleImport)
    const releaseNotesExecuteLambdaRole = Role.fromRoleArn(this, "releaseNotesExecuteLambdaRole", releaseNotesExecuteLambdaRoleImport)
    const jiraToken = Secret.fromSecretCompleteArn(this, "jiraToken", jiraTokenSecretImport)
    const confluenceToken = Secret.fromSecretCompleteArn(this, "confluenceToken", confluenceTokenSecretImport)

    const functions = new Functions(this, "Functions", {
      stackName: props.stackName || "ReleaseNotesStack",
      version: props.version,
      commitId: props.commitId,
      logRetentionInDays: 7,
      logLevel: "INFO",
      syncKnowledgeBaseManagedPolicy: undefined as any,
      preprocessingManagedPolicy: undefined as any,
      knowledgeBaseId: "",
      dataSourceId: "",
      region: "",
      account: "",
    })

    new Policies(this, "Policies", {
      jiraToken: jiraToken,
      confluenceToken: confluenceToken,
      createReleaseNotesFunction: functions.createReleaseNotesFunction,
      markJiraReleasedFunction: functions.markJiraReleasedFunction,
      releaseCutFunction: functions.releaseCutFunction,
      deployRole: deploymentRole,
      releaseNotesExecuteLambdaRole: releaseNotesExecuteLambdaRole
    })

    nagSuppressions(this, this.account)
  }
}
