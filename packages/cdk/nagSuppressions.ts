import {safeAddNagSuppression} from "@nhsdigital/eps-cdk-constructs"
import {Stack} from "aws-cdk-lib"

export const nagSuppressions = (stack: Stack) => {
  // Suppress wildcard log permissions for SyncKnowledgeBase Lambda
  safeAddNagSuppression(
    stack,
    "/ReleaseNotes/Policies/ExecuteLambdasManagedPolicy/Resource",
    [
      {
        id: "AwsSolutions-IAM5",
        reason: "Wildcard permissions are required for log stream access under known paths."
      }
    ]
  )
}
