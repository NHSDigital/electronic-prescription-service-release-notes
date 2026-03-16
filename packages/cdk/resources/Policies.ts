import {Construct} from "constructs"
import {PythonLambdaFunction} from "@nhsdigital/eps-cdk-constructs"
import {IRole, ManagedPolicy, PolicyStatement} from "aws-cdk-lib/aws-iam"
import {ISecret} from "aws-cdk-lib/aws-secretsmanager"

export interface PoliciesProps {
  readonly jiraToken: ISecret
  readonly confluenceToken: ISecret
  readonly createReleaseNotesFunction: PythonLambdaFunction
  readonly markJiraReleasedFunction: PythonLambdaFunction
  readonly releaseCutFunction: PythonLambdaFunction
  readonly deployRole: IRole
  readonly releaseNotesExecuteLambdaRole: IRole
}

export class Policies extends Construct {

  constructor(scope: Construct, id: string, props: PoliciesProps) {
    super(scope, id)
    const getSecretValue = new PolicyStatement({
      actions: [
        "secretsmanager:GetSecretValue"
      ],
      resources: [
        props.jiraToken.secretArn,
        props.confluenceToken.secretArn
      ]
    })
    new ManagedPolicy(this, "GetSecretValuePolicy", {
      description: "Policy to get secrets for Jira and Confluence tokens",
      statements: [
        getSecretValue
      ],
      roles: [
        props.createReleaseNotesFunction.executionRole,
        props.markJiraReleasedFunction.executionRole,
        props.releaseCutFunction.executionRole
      ]
    })

    const executeLambdasPolicy = new PolicyStatement({
      actions: [
        "lambda:InvokeFunction"
      ],
      resources: [
        props.createReleaseNotesFunction.function.functionArn,
        props.markJiraReleasedFunction.function.functionArn,
        props.releaseCutFunction.function.functionArn
      ]
    })
    const listExportsPolicy = new PolicyStatement({
      actions: [
        "cloudformation:ListExports"
      ],
      resources: ["*"]
    })
    new ManagedPolicy(this, "ExecuteLambdasManagedPolicy", {
      description: "Policy to allow invoking of release notes related Lambdas",
      statements: [
        executeLambdasPolicy,
        listExportsPolicy
      ],
      roles: [
        props.deployRole,
        props.releaseNotesExecuteLambdaRole
      ]
    })
  }
}
