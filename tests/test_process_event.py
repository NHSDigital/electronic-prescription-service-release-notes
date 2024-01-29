import unittest
from unittest.mock import patch
from create_release_notes import create_release_notes
from tests.common import (
    mocked_jira_get_issue,
    expected_rc_release_notes,
    mocked_compare,
    mocked_get_tags,
)


class TestProcessEvent(unittest.TestCase):
    @patch("create_release_notes.create_release_notes.Jira")
    @patch("create_release_notes.create_release_notes.Confluence")
    @patch("github.Repository.Repository")
    def test_create_rc_release_notes(self, mock_repository, mock_confluence, mock_jira):
        mock_jira.get_issue.side_effect = mocked_jira_get_issue
        mock_repository.get_tags.side_effect = mocked_get_tags
        mock_repository.compare.side_effect = mocked_compare

        event = {
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
        }

        create_release_notes.process_event(
            event=event,
            jira=mock_jira,
            repo=mock_repository,
            confluence=mock_confluence,
        )

        mock_confluence.create_page.assert_any_call(
            parent_id="734733361",
            title="TEST PfP-AWS-v1.0.442-beta - Deployed to [INT] on 29-01-24",
            body="\n".join(expected_rc_release_notes),
            space="APIMC",
        )


if __name__ == "__main__":
    unittest.main()
