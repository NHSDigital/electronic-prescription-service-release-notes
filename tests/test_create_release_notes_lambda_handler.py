import unittest
import os
from unittest.mock import patch
from create_release_notes import create_release_notes


class LambdaContext:
    aws_request_id = "abcdef"
    function_name = "test"
    log_stream_name = "1f73402ad"
    invoked_function_arn = "arn:aws:lambda:region:1000:function:TestCFStackNam-TestLambdaFunctionResourceName-ABC-1234F"
    client_context = None
    log_group_name = (
        "/aws/lambda/TestCFStackName-TestLambdaFunctionResourceName-ABC-1234F"
    )
    function_name = (
        "TestCloudFormationStackName-TestLambdaFunctionResourceName--ABC-1234F"
    )
    function_version = "$LATEST"
    identity = "<__main__.CognitoIdentity object at 0x1fb81abc00>"
    memory_limit_in_mb = "128"


context = LambdaContext()


def get_event(github_token=""):
    return {
        "createReleaseCandidate": "true",
        "releasePrefix": "PfP-AWS-",
        "currentTag": "tag_1",
        "targetTag": "tag_3",
        "repoName": "prescriptionsforpatients",
        "targetEnvironment": "INT",
        "productName": "EPS FHIR API",
        "releaseNotesPageId": "734733361",
        "releaseNotesPageTitle": "TEST PfP-AWS-v1.0.442-beta - Deployed to [INT] on 29-01-24",
        "releaseURL": "https://github.com/NHSDigital/prescriptionsforpatients/actions/runs/7692810696",
        "gitHubToken": github_token,
    }


class TestLambdaHandler(unittest.TestCase):
    @patch("create_release_notes.create_release_notes.process_event")
    @patch("create_release_notes.create_release_notes.Github")
    def test_create_release_notes_success(self, _mock_process_event, _mock_github):
        os.environ["JIRA_TOKEN"] = "JIRA_TOKEN"
        os.environ["CONFLUENCE_TOKEN"] = "CONFLUENCE_TOKEN"

        events = [
            get_event(),
            get_event("mocked_github_token"),
        ]

        for event in events:
            response = create_release_notes.lambda_handler(event=event, context=context)
            self.assertEqual(response, {"status": "OK", "statusCode": 200})

    @patch("create_release_notes.create_release_notes.process_event")
    @patch("create_release_notes.create_release_notes.Github")
    def test_create_release_notes_bad_event(self, _mock_process_event, _mock_github):
        event = {
            "bad_event": "test_release",
        }
        os.environ["JIRA_TOKEN"] = "JIRA_TOKEN"
        response = create_release_notes.lambda_handler(event=event, context=context)

        self.assertEqual(response["statusCode"], 400)


if __name__ == "__main__":
    unittest.main()
