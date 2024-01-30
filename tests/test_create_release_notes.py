import unittest
from unittest.mock import patch
from create_release_notes import create_release_notes
from tests.common import (
    mocked_jira_get_issue,
    expected_release_notes,
    expected_rc_release_notes_with_release_run_link,
    expected_rc_release_notes_with_no_release_run_link,
    mocked_compare,
    mocked_get_tags,
)


class TestGetJiraDetails(unittest.TestCase):
    @patch("create_release_notes.create_release_notes.Jira")
    def test_create_release_notes(self, mock_jira):
        mock_jira.get_issue.side_effect = mocked_jira_get_issue

        tags = mocked_get_tags()
        diff = mocked_compare()

        release_notes = create_release_notes.create_release_notes(
            jira=mock_jira,
            current_tag="tag_1",
            target_tag="tag_3",
            target_environment="INT",
            product_name="EPS FHIR API",
            create_release_candidate=False,
            release_name="v1.0.442-beta ",
            release_url="https://github.com/NHSDigital/prescriptionsforpatients/actions/runs/7692810696",
            diff=diff,
            tags=tags,
            repo_name="prescriptionsforpatients",
        )

        self.assertEqual(release_notes, expected_release_notes)

    @patch("create_release_notes.create_release_notes.Jira")
    def test_create_rc_release_notes_with_run_link(self, mock_jira):
        mock_jira.get_issue.side_effect = mocked_jira_get_issue

        tags = mocked_get_tags()
        diff = mocked_compare()

        release_notes = create_release_notes.create_release_notes(
            jira=mock_jira,
            current_tag="tag_1",
            target_tag="tag_3",
            target_environment="INT",
            product_name="EPS FHIR API",
            create_release_candidate=True,
            release_name="v1.0.442-beta ",
            release_url="https://github.com/NHSDigital/prescriptionsforpatients/actions/runs/7692810696",
            diff=diff,
            tags=tags,
            repo_name="prescriptionsforpatients",
        )

        self.assertEqual(release_notes, expected_rc_release_notes_with_release_run_link)
        # self.assertEqual(mock_jira.edit_issue.call_count, 2)
        # self.assertEqual(mock_jira.issue_transition.call_count, 2)

    @patch("create_release_notes.create_release_notes.Jira")
    def test_create_rc_release_notes_without_run_link(self, mock_jira):
        mock_jira.get_issue.side_effect = mocked_jira_get_issue

        tags = mocked_get_tags()
        diff = mocked_compare()

        release_notes = create_release_notes.create_release_notes(
            jira=mock_jira,
            current_tag="tag_1",
            target_tag="tag_3",
            target_environment="INT",
            product_name="EPS FHIR API",
            create_release_candidate=True,
            release_url=None,
            release_name="v1.0.442-beta ",
            diff=diff,
            tags=tags,
            repo_name="prescriptionsforpatients",
        )

        self.assertEqual(
            release_notes, expected_rc_release_notes_with_no_release_run_link
        )
        # self.assertEqual(mock_jira.edit_issue.call_count, 2)
        # self.assertEqual(mock_jira.issue_transition.call_count, 2)


if __name__ == "__main__":
    unittest.main()
