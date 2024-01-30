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

param_list = [
    ("normal release notes", False, None, 0, 0, expected_release_notes),
    (
        "rc release notes with release url",
        True,
        "https://github.com/NHSDigital/prescriptionsforpatients/actions/runs/7692810696",
        2,
        2,
        expected_rc_release_notes_with_release_run_link,
    ),
    (
        "rc release notes without release url",
        True,
        None,
        2,
        2,
        expected_rc_release_notes_with_no_release_run_link,
    ),
]


class TestGetJiraDetails(unittest.TestCase):
    @patch("create_release_notes.create_release_notes.Jira")
    def test_create_release_notes(self, mock_jira):
        tags = mocked_get_tags()
        diff = mocked_compare()
        for (
            scenario,
            create_release_candidate,
            release_url,
            edit_issue_call_count,
            issue_transition_call_count,
            expected_output,
        ) in param_list:
            with self.subTest(
                msg=scenario,
            ):
                mock_jira.reset_mock()
                mock_jira.get_issue.side_effect = mocked_jira_get_issue
                release_notes = create_release_notes.create_release_notes(
                    jira=mock_jira,
                    current_tag="tag_1",
                    target_tag="tag_3",
                    target_environment="INT",
                    product_name="EPS FHIR API",
                    create_release_candidate=create_release_candidate,
                    release_name="v1.0.442-beta ",
                    release_url=release_url,
                    diff=diff,
                    tags=tags,
                    repo_name="prescriptionsforpatients",
                )

                self.assertEqual(release_notes, expected_output)
                self.assertEqual(mock_jira.edit_issue.call_count, edit_issue_call_count)
                self.assertEqual(
                    mock_jira.issue_transition.call_count, issue_transition_call_count
                )


if __name__ == "__main__":
    unittest.main()
