import unittest
from unittest.mock import patch
from create_release_notes import create_release_notes
from github import Comparison, Tag


def mocked_jira_get_issue(*args, **kwargs):
    if args[0] == "AEA-123":
        return {
            "fields": {
                "summary": "Test Summary",
                "description": "User story\nTest User Story\nBackground: Test Background",
                "components": [{"name": "Component1"}, {"name": "Component2"}],
                "customfield_26905": {"value": "High"},
                "customfield_13618": "Service Impact",
            }
        }
    elif args[0] == "AEA-124":
        return {
            "fields": {
                "summary": "Test Summary",
                "description": "Background: Test Background",
                "components": [{"name": "Component1"}, {"name": "Component2"}],
                "customfield_26905": {"value": "High"},
                "customfield_13618": "Service Impact",
            }
        }
    elif args[0] == "AEA-125":
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
    def test_create_release_notes(self, mock_jira):
        mock_jira.get_issue.side_effect = mocked_jira_get_issue

        tag_1 = Tag.Tag(None, None, {"name": "tag_1", "commit": {"sha": "sha_1"}}, True)
        tag_2 = Tag.Tag(None, None, {"name": "tag_2", "commit": {"sha": "sha_2"}}, True)
        tag_3 = Tag.Tag(None, None, {"name": "tag_3", "commit": {"sha": "sha_3"}}, True)
        tags = [tag_1, tag_2, tag_3]

        comparison_details = {
            "url": "https://api.github.com/repos/NHSDigital/electronic-prescription-service-api/compare/v1.0.1692-beta...v1.0.1693-beta",
            "commits": [
                {
                    "sha": "sha_1",
                    "commit": {"message": "AEA-123"},
                },
                {
                    "sha": "sha_2",
                    "commit": {"message": "no jira"},
                },
                {
                    "sha": "sha_3",
                    "commit": {"message": "AEA-124"},
                },
            ],
        }

        diff = Comparison.Comparison("", None, comparison_details, True)

        release_notes = create_release_notes.create_release_notes(
            jira=mock_jira,
            current_tag="tag_1",
            target_tag="tag_3",
            target_environment="dev",
            product_name="EPS FHIR API",
            create_release_candidate=False,
            release_name="v1.0.442-beta ",
            release_url="https://github.com/NHSDigital/prescriptionsforpatients/actions/runs/7692810696",
            diff=diff,
            tags=tags,
            repo_name="prescriptionsforpatients",
        )

        expected_release_notes = [
            "This page is auto generated. Any manual modifications will be lost",
            "<h1 id='Currentreleasenotestag_3-plannedreleasetotagtag_3'>EPS FHIR API planned release to dev of tag tag_3</h1>",
            "<h2 id='Currentreleasenotestag_3-Changessincecurrentlyreleasedtagtag_1'>Changes since currently released tag tag_1</h2>",
            "<p>***",
            "<br/>jira link               : <a class='external-link' href='https://nhsd-jira.digital.nhs.uk/browse/AEA-123' rel='nofollow'>https://nhsd-jira.digital.nhs.uk/browse/AEA-123</a>",
            "<br/>jira title              : Test Summary",
            "<br/>user story              : Test User Story",
            "<br/>commit title            : AEA-123",
            "<br/>release tag             : tag_1",
            "<br/>github release          : <a class='external-link' href='https://github.com/NHSDigital/prescriptionsforpatients/releases/tag/tag_1' rel='nofollow'>https://github.com/NHSDigital/prescriptionsforpatients/releases/tag/tag_1</a>",
            "<br/>Area affected           : ['Component1', 'Component2']",
            "<br/>Impact                  : High",
            "<br/>Business/Service Impact : Service Impact",
            "</p>",
            "<p>***",
            "<br/>jira link               : n/a",
            "<br/>jira title              : n/a",
            "<br/>user story              : n/a",
            "<br/>commit title            : no jira",
            "<br/>release tag             : tag_2",
            "<br/>github release          : <a class='external-link' href='https://github.com/NHSDigital/prescriptionsforpatients/releases/tag/tag_2' rel='nofollow'>https://github.com/NHSDigital/prescriptionsforpatients/releases/tag/tag_2</a>",
            "<br/>Area affected           : []",
            "<br/>Impact                  : n/a",
            "<br/>Business/Service Impact : n/a",
            "</p>",
            "<p>***",
            "<br/>jira link               : <a class='external-link' href='https://nhsd-jira.digital.nhs.uk/browse/AEA-124' rel='nofollow'>https://nhsd-jira.digital.nhs.uk/browse/AEA-124</a>",
            "<br/>jira title              : Test Summary",
            "<br/>user story              : can not find user story",
            "<br/>commit title            : AEA-124",
            "<br/>release tag             : tag_3",
            "<br/>github release          : <a class='external-link' href='https://github.com/NHSDigital/prescriptionsforpatients/releases/tag/tag_3' rel='nofollow'>https://github.com/NHSDigital/prescriptionsforpatients/releases/tag/tag_3</a>",
            "<br/>Area affected           : ['Component1', 'Component2']",
            "<br/>Impact                  : High",
            "<br/>Business/Service Impact : Service Impact",
            "</p>",
        ]
        self.assertEqual(release_notes, expected_release_notes)

    @patch("create_release_notes.create_release_notes.Jira")
    def test_create_rc_release_notes(self, mock_jira):
        mock_jira.get_issue.side_effect = mocked_jira_get_issue

        tag_1 = Tag.Tag(None, None, {"name": "tag_1", "commit": {"sha": "sha_1"}}, True)
        tag_2 = Tag.Tag(None, None, {"name": "tag_2", "commit": {"sha": "sha_2"}}, True)
        tag_3 = Tag.Tag(None, None, {"name": "tag_3", "commit": {"sha": "sha_3"}}, True)
        tags = [tag_1, tag_2, tag_3]

        comparison_details = {
            "url": "https://api.github.com/repos/NHSDigital/electronic-prescription-service-api/compare/v1.0.1692-beta...v1.0.1693-beta",
            "commits": [
                {
                    "sha": "sha_1",
                    "commit": {"message": "AEA-123"},
                },
                {
                    "sha": "sha_2",
                    "commit": {"message": "no jira"},
                },
                {
                    "sha": "sha_3",
                    "commit": {"message": "AEA-124"},
                },
            ],
        }

        diff = Comparison.Comparison("", None, comparison_details, True)

        release_notes = create_release_notes.create_release_notes(
            jira=mock_jira,
            current_tag="tag_1",
            target_tag="tag_3",
            target_environment="dev",
            product_name="EPS FHIR API",
            create_release_candidate=True,
            release_name="v1.0.442-beta ",
            release_url="https://github.com/NHSDigital/prescriptionsforpatients/actions/runs/7692810696",
            diff=diff,
            tags=tags,
            repo_name="prescriptionsforpatients",
        )

        expected_release_notes = [
            "Release url: <a class='external-link' href='https://github.com/NHSDigital/prescriptionsforpatients/actions/runs/7692810696' rel='nofollow'>https://github.com/NHSDigital/prescriptionsforpatients/actions/runs/7692810696</a>",
            "<h1 id='Currentreleasenotestag_3-plannedreleasetotagtag_3'>EPS FHIR API planned release to dev of tag tag_3</h1>",
            "<h2 id='Currentreleasenotestag_3-Changessincecurrentlyreleasedtagtag_1'>Changes since currently released tag tag_1</h2>",
            "Changes with jira tickets",
            "<p>***",
            "<br/>jira link               : <a class='external-link' href='https://nhsd-jira.digital.nhs.uk/browse/AEA-123' rel='nofollow'>https://nhsd-jira.digital.nhs.uk/browse/AEA-123</a>",
            "<br/>jira title              : Test Summary",
            "<br/>user story              : Test User Story",
            "<br/>commit title            : AEA-123",
            "<br/>release tag             : tag_1",
            "<br/>github release          : <a class='external-link' href='https://github.com/NHSDigital/prescriptionsforpatients/releases/tag/tag_1' rel='nofollow'>https://github.com/NHSDigital/prescriptionsforpatients/releases/tag/tag_1</a>",
            "<br/>Area affected           : ['Component1', 'Component2']",
            "<br/>Impact                  : High",
            "<br/>Business/Service Impact : Service Impact",
            "</p>",
            "<p>***",
            "<br/>jira link               : <a class='external-link' href='https://nhsd-jira.digital.nhs.uk/browse/AEA-124' rel='nofollow'>https://nhsd-jira.digital.nhs.uk/browse/AEA-124</a>",
            "<br/>jira title              : Test Summary",
            "<br/>user story              : can not find user story",
            "<br/>commit title            : AEA-124",
            "<br/>release tag             : tag_3",
            "<br/>github release          : <a class='external-link' href='https://github.com/NHSDigital/prescriptionsforpatients/releases/tag/tag_3' rel='nofollow'>https://github.com/NHSDigital/prescriptionsforpatients/releases/tag/tag_3</a>",
            "<br/>Area affected           : ['Component1', 'Component2']",
            "<br/>Impact                  : High",
            "<br/>Business/Service Impact : Service Impact",
            "</p>",
            "Changes without jira tickets",
            "<p>***",
            "<br/>jira link               : n/a",
            "<br/>jira title              : n/a",
            "<br/>user story              : n/a",
            "<br/>commit title            : no jira",
            "<br/>release tag             : tag_2",
            "<br/>github release          : <a class='external-link' href='https://github.com/NHSDigital/prescriptionsforpatients/releases/tag/tag_2' rel='nofollow'>https://github.com/NHSDigital/prescriptionsforpatients/releases/tag/tag_2</a>",
            "<br/>Area affected           : []",
            "<br/>Impact                  : n/a",
            "<br/>Business/Service Impact : n/a",
            "</p>",
        ]
        self.assertEqual(release_notes, expected_release_notes)
        # self.assertEqual(mock_jira.edit_issue.call_count, 2)
        # self.assertEqual(mock_jira.issue_transition.call_count, 2)


if __name__ == "__main__":
    unittest.main()
