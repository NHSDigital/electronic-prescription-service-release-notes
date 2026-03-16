import {Construct} from "constructs"
import {PythonLambdaFunction} from "@nhsdigital/eps-cdk-constructs"
import {resolve} from "path"

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

    // Lambda function to create release notes
    const createReleaseNotesFunction = new PythonLambdaFunction(this, "CreateReleaseNotesFunction", {
      functionName: `${props.stackName}-CreateReleaseNotesFunction`,
      projectBaseDir: resolve(__dirname, "../../.."),
      packageBasePath: "packages/create_release_notes",
      handler: "app.handler.handler",
      logRetentionInDays: props.logRetentionInDays,
      logLevel: props.logLevel,
      dependencyLocation: ".dependencies/create_release_notes"
    })

    // Lambda function to create release notes
    const markJiraReleasedFunction = new PythonLambdaFunction(this, "MarkJiraReleasedFunction", {
      functionName: `${props.stackName}-MarkJiraReleasedFunction`,
      projectBaseDir: resolve(__dirname, "../../.."),
      packageBasePath: "packages/mark_jira_released",
      handler: "app.handler.handler",
      logRetentionInDays: props.logRetentionInDays,
      logLevel: props.logLevel,
      dependencyLocation: ".dependencies/mark_jira_released"
    })

    // Lambda function to create release notes
    const releaseCutFunction = new PythonLambdaFunction(this, "ReleaseCutFunction", {
      functionName: `${props.stackName}-ReleaseCutFunction`,
      projectBaseDir: resolve(__dirname, "../../.."),
      packageBasePath: "packages/release_cut",
      handler: "app.handler.handler",
      logRetentionInDays: props.logRetentionInDays,
      logLevel: props.logLevel,
      dependencyLocation: ".dependencies/release_cut"
    })
    this.createReleaseNotesFunction = createReleaseNotesFunction
    this.markJiraReleasedFunction = markJiraReleasedFunction
    this.releaseCutFunction = releaseCutFunction
  }
}
