#!/usr/bin/env bash

cat <<EOF > payload.json
{ 
  "currentTag": "$CURRENT_DEPLOYED_TAG",
  "targetTag": "$RELEASE_TAG",
  "repoName": "$REPO_NAME",
  "targetEnvironment": "$TARGET_ENV",
  "productName": "$PRODUCT_NAME",
  "releaseNotesPageId": "$PAGE_ID",
  "releaseNotesPageTitle": "$RELEASE_PREFIX-$RELEASE_TAG - Deployed to [$TARGET_ENV] on $(date +'%d-%m-%y')",
  "createReleaseCandidate": "true",
  "releasePrefix": "$RELEASE_PREFIX-"
}
EOF
cat payload.json

# function_arn=$(aws cloudformation list-exports --query "Exports[?Name=='release-notes:CreateReleaseNotesLambdaArn'].Value" --output text)
# aws lambda invoke --function-name "${function_arn}" --cli-binary-format raw-in-base64-out --payload file://payload.json out.txt
aws lambda invoke --function-name "arn:aws:lambda:eu-west-2:591291862413:function:release-notes-pr-306-createReleaseNotes" --cli-binary-format raw-in-base64-out --payload file://payload.json out.txt
cat out.txt

status_code=$(jq -r '.statusCode' out.txt)
if [[ ! "$status_code" =~ ^2[0-9][0-9]$ ]]; then
  echo "Error: Lambda returned non-2xx statusCode: $status_code"
  exit 1
fi
