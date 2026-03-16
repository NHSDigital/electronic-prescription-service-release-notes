import {Construct} from "constructs"
import {PythonLambdaFunction} from "@nhsdigital/eps-cdk-constructs"
import {resolve} from "path"
import {ManagedPolicy} from "aws-cdk-lib/aws-iam"
import {Fn} from "aws-cdk-lib"

export interface FunctionsProps {
  readonly stackName: string
  readonly version: string
  readonly commitId: string
  readonly logRetentionInDays: number
  readonly logLevel: string
}

export class Functions extends Construct {
  public readonly createReleaseNotesFunction: PythonLambdaFunction
  public readonly markJiraReleasedFunction: PythonLambdaFunction
  public readonly releaseCutFunction: PythonLambdaFunction

  constructor(scope: Construct, id: string, props: FunctionsProps) {
    super(scope, id)

    const lambdaDecryptSecretsKMSPolicy = ManagedPolicy.fromManagedPolicyArn(
      scope, "lambdaDecryptSecretsKMSPolicy", Fn.importValue("account-resources:LambdaDecryptSecretsKMSPolicy"))

    // Lambda function to create release notes
    const createReleaseNotesFunction = new PythonLambdaFunction(this, "CreateReleaseNotesFunction", {
      functionName: `${props.stackName}-CreateReleaseNotesFunction`,
      projectBaseDir: resolve(__dirname, "../../.."),
      packageBasePath: "packages/create_release_notes",
      handler: "app.create_release_notes.lambda_handler",
      logRetentionInDays: props.logRetentionInDays,
      logLevel: props.logLevel,
      dependencyLocation: ".dependencies/create_release_notes",
      additionalPolicies: [lambdaDecryptSecretsKMSPolicy]
    })

    // Lambda function to create release notes
    const markJiraReleasedFunction = new PythonLambdaFunction(this, "MarkJiraReleasedFunction", {
      functionName: `${props.stackName}-MarkJiraReleasedFunction`,
      projectBaseDir: resolve(__dirname, "../../.."),
      packageBasePath: "packages/mark_jira_released",
      handler: "app.mark_jira_released.lambda_handler",
      logRetentionInDays: props.logRetentionInDays,
      logLevel: props.logLevel,
      dependencyLocation: ".dependencies/mark_jira_released",
      additionalPolicies: [lambdaDecryptSecretsKMSPolicy]
    })

    // Lambda function to create release notes
    const releaseCutFunction = new PythonLambdaFunction(this, "ReleaseCutFunction", {
      functionName: `${props.stackName}-ReleaseCutFunction`,
      projectBaseDir: resolve(__dirname, "../../.."),
      packageBasePath: "packages/release_cut",
      handler: "app.release_cut.lambda_handler",
      logRetentionInDays: props.logRetentionInDays,
      logLevel: props.logLevel,
      dependencyLocation: ".dependencies/release_cut",
      additionalPolicies: [lambdaDecryptSecretsKMSPolicy]
    })
    this.createReleaseNotesFunction = createReleaseNotesFunction
    this.markJiraReleasedFunction = markJiraReleasedFunction
    this.releaseCutFunction = releaseCutFunction
  }
}
