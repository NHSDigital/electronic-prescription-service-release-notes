import unittest
from unittest.mock import patch
from create_release_notes import create_release_notes


class TestGetJiraDetails(unittest.TestCase):
    @patch("create_release_notes.create_release_notes.Jira")
    def test_get_jira_details_success(self, mock_jira):
        jira_instance = mock_jira.return_value
        jira_instance.get_issue.return_value = {
            "fields": {
                "summary": "Test Summary",
                "description": "User story\nTest User Story\nBackground: Test Background",
                "components": [{"name": "Component1"}, {"name": "Component2"}],
                "customfield_26905": {"value": "High"},
                "customfield_13618": "Service Impact",
            }
        }

        (
            jira_title,
            user_story,
            components,
            impact,
            business_service_impact,
        ) = create_release_notes.get_jira_details(jira_instance, "TEST-123")

        self.assertEqual(jira_title, "Test Summary")
        self.assertEqual(user_story, "Test User Story")
        self.assertEqual(components, ["Component1", "Component2"])
        self.assertEqual(impact, "High")
        self.assertEqual(business_service_impact, "Service Impact")

    @patch("create_release_notes.create_release_notes.Jira")
    def test_get_jira_details_no_user_story(self, mock_jira):
        jira_instance = mock_jira.return_value
        jira_instance.get_issue.return_value = {
            "fields": {
                "summary": "Test Summary",
                "description": "Background: Test Background",
                "components": [{"name": "Component1"}, {"name": "Component2"}],
                "customfield_26905": {"value": "High"},
                "customfield_13618": "Service Impact",
            }
        }

        result = create_release_notes.get_jira_details(jira_instance, "TEST-123")

        self.assertEqual(result[1], "can not find user story")

    @patch("create_release_notes.create_release_notes.Jira")
    def test_get_jira_details_no_impact(self, mock_jira):
        jira_instance = mock_jira.return_value
        jira_instance.get_issue.return_value = {
            "fields": {
                "summary": "Test Summary",
                "description": "User story: Test User Story\nBackground: Test Background",
                "components": [{"name": "Component1"}, {"name": "Component2"}],
                "customfield_13618": "Service Impact",
            }
        }

        result = create_release_notes.get_jira_details(jira_instance, "TEST-123")

        self.assertEqual(result[3], "")

    @patch("create_release_notes.create_release_notes.Jira")
    def test_get_jira_details_exception(self, mock_jira):
        jira_instance = mock_jira.return_value
        jira_instance.get_issue.side_effect = Exception("Something went wrong")

        result = create_release_notes.get_jira_details(jira_instance, "TEST-123")

        self.assertEqual(result[0], "can not find jira ticket for TEST-123")


if __name__ == "__main__":
    unittest.main()
