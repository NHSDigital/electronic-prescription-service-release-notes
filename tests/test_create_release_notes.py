import unittest
from unittest.mock import patch
from create_release_notes import create_release_notes

test_commit = """
    {"commit": {
        "message": "Remove completion functions from GitAuthor"
    },
    "sha": "1292bf0e22c796e91cc3d6e24b544aece8c21f2a"
    }
"""


def mocked_jira_get_issue(*args, **kwargs):
    if args[0] == "TEST-123":
        return {
            "fields": {
                "summary": "Test Summary",
                "description": "User story\nTest User Story\nBackground: Test Background",
                "components": [{"name": "Component1"}, {"name": "Component2"}],
                "customfield_26905": {"value": "High"},
                "customfield_13618": "Service Impact",
            }
        }
    elif args[0] == "TEST-124":
        return {
            "fields": {
                "summary": "Test Summary",
                "description": "Background: Test Background",
                "components": [{"name": "Component1"}, {"name": "Component2"}],
                "customfield_26905": {"value": "High"},
                "customfield_13618": "Service Impact",
            }
        }
    elif args[0] == "TEST-125":
        return {
            "fields": {
                "summary": "Test Summary",
                "description": "User story\nTest User Story\nBackground: Test Background",
                "components": [{"name": "Component1"}, {"name": "Component2"}],
                "customfield_13618": "Service Impact",
            }
        }
    else:
        raise (Exception)


class TestGetJiraDetails(unittest.TestCase):
    @patch("create_release_notes.create_release_notes.Jira")
    def test_get_jira_details_success(self, mock_jira):
        mock_jira.get_issue.side_effect = mocked_jira_get_issue

        jira_details = create_release_notes.get_jira_details(mock_jira, "TEST-123")

        self.assertEqual(jira_details.jira_title, "Test Summary")
        self.assertEqual(jira_details.user_story, "Test User Story")
        self.assertEqual(jira_details.components, ["Component1", "Component2"])
        self.assertEqual(jira_details.impact, "High")
        self.assertEqual(jira_details.business_service_impact, "Service Impact")


if __name__ == "__main__":
    unittest.main()
