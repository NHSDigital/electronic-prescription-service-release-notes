import unittest
from unittest.mock import patch, MagicMock
from release_cut.release_cut import (
    process_event,
    add_fix_version_to_jira,
    lambda_handler,
)


class TestReleaseCut(unittest.TestCase):
    @patch("release_cut.release_cut.Jira")
    def test_add_fix_version_to_jira(self, MockJira):
        mock_jira = MockJira()
        tickets = ["AEA-1234", "AEA-5678"]
        release_name = "v1.0.0"

        add_fix_version_to_jira(mock_jira, release_name, tickets)

        for ticket in tickets:
            mock_jira.edit_issue.assert_any_call(
                issue_id_or_key=ticket,
                fields={"fixVersions": [{"add": {"name": release_name}}]},
            )

    @patch("release_cut.release_cut.Jira")
    def test_process_event(self, MockJira):
        mock_jira = MockJira()
        event = {
            "releaseTag": "v1.0.0",
            "releasePrefix": "prefix",
            "tickets": ["AEA-1234", "AEA-5678"],
        }

        process_event(event, mock_jira)

        mock_jira.add_version.assert_called_once_with(
            project_key="AEA",
            project_id="15116",
            version="prefix-v1.0.0",
        )

        for ticket in event["tickets"]:
            mock_jira.edit_issue.assert_any_call(
                issue_id_or_key=ticket,
                fields={"fixVersions": [{"add": {"name": "prefix-v1.0.0"}}]},
            )

    @patch("release_cut.release_cut.validate")
    @patch("release_cut.release_cut.Jira")
    @patch("release_cut.release_cut.parameters.get_secret")
    @patch("release_cut.release_cut.os.getenv")
    def test_lambda_handler(
        self, mock_getenv, mock_get_secret, MockJira, mock_validate
    ):
        mock_getenv.side_effect = lambda key: (
            "mocked_token" if key == "JIRA_TOKEN" else None
        )
        mock_get_secret.return_value = "mocked_token"
        mock_jira = MockJira()
        mock_validate.return_value = None

        event = {
            "releaseTag": "v1.0.0",
            "releasePrefix": "prefix",
            "tickets": ["AEA-1234", "AEA-5678"],
        }
        context = MagicMock()

        response = lambda_handler(event, context)

        self.assertEqual(response, {"status": "OK", "statusCode": 200})
        mock_getenv.assert_any_call("JIRA_TOKEN")
        mock_get_secret.assert_called_with("account-resources-jiraToken")
        mock_jira.assert_called_once_with(
            "https://nhsd-jira.digital.nhs.uk/",
            token="mocked_token",
            session=unittest.mock.ANY,
        )


if __name__ == "__main__":
    unittest.main()
