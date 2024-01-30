import unittest
from unittest.mock import patch
from datetime import datetime
from mark_jira_released import mark_jira_released


class TestProcessEvent(unittest.TestCase):
    @patch("mark_jira_released.mark_jira_released.Jira")
    def test_mark_jira_released_success(self, mock_jira):
        mock_jira.get_project_versions.return_value = [
            {"name": "test_release", "id": "1234"},
            {"name": "another_release", "id": "5678"},
        ]

        event = {
            "releaseVersion": "test_release",
        }

        mark_jira_released.process_event(event=event, jira=mock_jira)

        mock_jira.update_version.assert_any_call(
            version="1234",
            is_released=True,
            release_date=datetime.today().strftime("%Y-%m-%d"),
        )

    @patch("mark_jira_released.mark_jira_released.Jira")
    def test_mark_jira_released_no_release(self, mock_jira):
        mock_jira.get_project_versions.return_value = [
            {"name": "test_release", "id": "1234"},
            {"name": "another_release", "id": "5678"},
        ]

        event = {
            "releaseVersion": "test_release_does_not_exist",
        }

        with self.assertRaises(Exception) as context:
            mark_jira_released.process_event(event=event, jira=mock_jira)

        mock_jira.update_version.assert_not_called()
        self.assertTrue(
            "can not find release version for test_release_does_not_exist"
            in str(context.exception)
        )


if __name__ == "__main__":
    unittest.main()
