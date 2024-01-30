import unittest
import os
from unittest.mock import patch
from mark_jira_released import mark_jira_released


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


class TestLambdaHandler(unittest.TestCase):
    @patch("mark_jira_released.mark_jira_released.process_event")
    def test_mark_jira_released_success(self, mock_process_event):
        event = {
            "releaseVersion": "test_release",
        }
        os.environ["JIRA_TOKEN"] = "JIRA_TOKEN"
        response = mark_jira_released.lambda_handler(event=event, context=context)

        self.assertEqual(response, {"status": "OK", "statusCode": 200})

    @patch("mark_jira_released.mark_jira_released.process_event")
    def test_mark_jira_released_bad_event(self, mock_process_event):
        event = {
            "bad_event": "test_release",
        }
        os.environ["JIRA_TOKEN"] = "JIRA_TOKEN"
        response = mark_jira_released.lambda_handler(event=event, context=context)

        self.assertEqual(response["statusCode"], 400)


if __name__ == "__main__":
    unittest.main()
