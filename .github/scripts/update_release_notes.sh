#!/usr/bin/env bash

cat <<EOF > payload.json
{ 
  "currentTag": "$CURRENT_DEPLOYED_TAG",
  "targetTag": "$RELEASE_TAG",
  "repoName": "$REPO_NAME",
  "targetEnvironment": "$TARGET_ENV",
  "productName": "$PRODUCT_NAME",
  "releaseNotesPageId": "$PAGE_ID",
  "releaseNotesPageTitle": "Current $REPO_NAME release notes - $TARGET_ENV"
}
EOF
cat payload.json

function_arn=$(aws cloudformation list-exports --query "Exports[?Name=='release-notes:CreateReleaseNotesLambdaArn'].Value" --output text)
aws lambda invoke --function-name "${function_arn}" --cli-binary-format raw-in-base64-out --payload file://payload.json out.txt
cat out.txt
