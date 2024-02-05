from github import Tag, Comparison


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
    elif args[0] == "AEA-126":
        return {
            "fields": {
                "summary": "Test Summary",
                "description": "User story\nit should not use this user story\nBackground: Test Background",
                "components": [{"name": "Component1"}, {"name": "Component2"}],
                "customfield_26905": {"value": "High"},
                "customfield_13618": "Service Impact",
                "customfield_17101": "This is the user story that should be used\nover two lines",
            }
        }
    else:
        raise (Exception)


def mocked_get_tags(*args, **kwargs):
    tag_1 = Tag.Tag(None, None, {"name": "tag_1", "commit": {"sha": "sha_1"}}, True)
    tag_2 = Tag.Tag(None, None, {"name": "tag_2", "commit": {"sha": "sha_2"}}, True)
    tag_3 = Tag.Tag(None, None, {"name": "tag_3", "commit": {"sha": "sha_3"}}, True)
    tags = [tag_1, tag_2, tag_3]
    return tags


def mocked_compare(*args, **kwargs):
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
    return diff


expected_release_notes = [
    "This page is auto generated. Any manual modifications will be lost",
    "<h1 id='Currentreleasenotestag_3-plannedreleasetotagtag_3'>EPS FHIR API planned release to INT of tag tag_3</h1>",
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


expected_rc_release_notes_with_release_run_link = [
    "Azure or github release run URL: <a class='external-link' href='https://github.com/NHSDigital/prescriptionsforpatients/actions/runs/7692810696' rel='nofollow'>https://github.com/NHSDigital/prescriptionsforpatients/actions/runs/7692810696</a>",
    "<h1 id='Currentreleasenotestag_3-plannedreleasetotagtag_3'>EPS FHIR API planned release to INT of tag tag_3</h1>",
    "<h2 id='Currentreleasenotestag_3-Changessincecurrentlyreleasedtagtag_1'>Changes since currently released tag tag_1</h2>",
    "<h3 id='jira_changes'>Changes with jira tickets</h3>",
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
    "<p>***</p>",
    "<h3 id='non_jira_changes'>Changes without jira tickets</h3>",
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

expected_rc_release_notes_with_no_release_run_link = [
    "<h1 id='Currentreleasenotestag_3-plannedreleasetotagtag_3'>EPS FHIR API planned release to INT of tag tag_3</h1>",
    "<h2 id='Currentreleasenotestag_3-Changessincecurrentlyreleasedtagtag_1'>Changes since currently released tag tag_1</h2>",
    "<h3 id='jira_changes'>Changes with jira tickets</h3>",
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
    "<p>***</p>",
    "<h3 id='non_jira_changes'>Changes without jira tickets</h3>",
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
