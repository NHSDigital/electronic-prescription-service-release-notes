import os
import re
from atlassian import Jira, Confluence  # type: ignore
from typing import NamedTuple
import traceback
import sys
from github import Github, Auth, Comparison, PaginatedList, Tag, Repository
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import SchemaValidationError, validate
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities import parameters
from html import escape

JIRA_URL = "https://nhsd-jira.digital.nhs.uk/"
CONFLUENCE_URL = "https://nhsd-confluence.digital.nhs.uk/"
logger = Logger()

INPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft-07/schema",
    "$id": "https://example.com/example.json",
    "type": "object",
    "title": "Sample schema",
    "description": "The root schema comprises the entire JSON document.",
    "examples": [
        {
            "currentTag": "v1.0.104-beta",
            "targetTag": "v1.0.120-beta",
            "repoName": "prescriptionsforpatients",
            "targetEnvironment": "PROD",
            "productName": "Prescriptions for Patients AWS layer",
            "releaseNotesPageId": "693750029",
            "releaseNotesPageTitle": "Current PfP AWS layer release notes - PROD",
            "releaseURL": "https://github.com/NHSDigital/prescriptionsforpatients/actions/runs/7081875172",
        }
    ],
    "required": [
        "currentTag",
        "targetTag",
        "repoName",
        "targetEnvironment",
        "productName",
        "releaseNotesPageId",
        "releaseNotesPageTitle",
    ],
    "properties": {
        "currentTag": {
            "$id": "#/properties/currentTag",
            "type": "string",
            "title": "The current tag to search for in github",
            "examples": ["v1.0.104-beta"],
        },
        "targetTag": {
            "$id": "#/properties/targetTag",
            "type": "string",
            "title": "The target tag to search for in github",
            "examples": ["v1.0.104-beta"],
        },
        "repoName": {
            "$id": "#/properties/repoName",
            "type": "string",
            "title": "The repo name in github to search for tags. Should NOT have NHSDigital in front of it",
            "examples": ["prescriptionsforpatients"],
        },
        "targetEnvironment": {
            "$id": "#/properties/targetEnvironment",
            "type": "string",
            "title": "The target environment. Used to construct details in confluence page",
            "examples": ["PROD"],
        },
        "productName": {
            "$id": "#/properties/productName",
            "type": "string",
            "title": "The product name. Used to construct details in confluence page",
            "examples": ["Prescriptions for Patients AWS layer"],
        },
        "releaseNotesPageId": {
            "$id": "#/properties/releaseNotesPageId",
            "type": "string",
            "title": "The release notes page id to update (for non RC release notes pages) or create page under (for RC release notes)",
            "examples": ["693750029"],
        },
        "releaseNotesPageTitle": {
            "$id": "#/properties/releaseNotesPageTitle",
            "type": "string",
            "title": "The release notes page title to update or create in confluence. This MUST be unique in the space for RC release notes",
            "examples": ["Current PfP AWS layer release notes - PROD"],
        },
        "createReleaseCandidate": {
            "$id": "#/properties/createReleaseCandidate",
            "type": "string",
            "title": "<OPTIONAL> Whether to create a release candidate page",
            "examples": ["true"],
        },
        "releasePrefix": {
            "$id": "#/properties/releasePrefix",
            "type": "string",
            "title": """
            <OPTIONAL> Prefix for the release in jira. The release created in jira has the format <releasePrefix><targetTag>.
            Only used when createReleaseCandidate=true
            """,
            "examples": [
                "https://github.com/NHSDigital/prescriptionsforpatients/actions/runs/7081875172"
            ],
        },
        "releaseURL": {
            "$id": "#/properties/releaseURL",
            "type": "string",
            "title": """
            <OPTIONAL> URL for the release workflow.
            Only used when createReleaseCandidate=true
            """,
            "examples": [
                "https://github.com/NHSDigital/prescriptionsforpatients/actions/runs/7692810696"
            ],
        },
    },
}


class JiraDetails(NamedTuple):
    jira_title: str
    user_story: str
    components: list[str]
    impact: str
    business_service_impact: str


def get_jira_details(jira: Jira, jira_ticket_number: str) -> JiraDetails:
    try:
        jira_ticket = jira.get_issue(jira_ticket_number)
        jira_title = jira_ticket["fields"]["summary"]
        jira_description = jira_ticket["fields"]["description"]
        components = [
            component["name"] for component in jira_ticket["fields"]["components"]
        ]
        user_story = jira_ticket["fields"].get("customfield_17101")
        if user_story is None or user_story == "":
            match = match = re.search(
                r"(user story)(.*?)background",
                jira_description,
                re.IGNORECASE | re.MULTILINE | re.DOTALL,
            )
            if match:
                user_story = match.group(2).replace("*", "").replace("h3.", "")
            else:
                user_story = "can not find user story"
        user_story = user_story.strip()
        impact_field = jira_ticket.get("fields", {}).get("customfield_26905", {})
        if impact_field:
            impact = impact_field.get("value", "")
        else:
            impact = ""
        business_service_impact = jira_ticket["fields"].get("customfield_13618") or ""
        return JiraDetails(
            jira_title, user_story, components, impact, business_service_impact
        )
    except:  # noqa: E722
        logger.error(traceback.format_exception(*sys.exc_info()))
        logger.error(f"problem getting details for {jira_ticket_number}")
        return JiraDetails(
            f"can not find jira ticket for {jira_ticket_number}", "", [], "", ""
        )


def create_release_notes(
    jira: Jira,
    current_tag: str,
    target_tag: str,
    target_environment: str,
    product_name: str,
    create_release_candidate: bool,
    release_name: str,
    release_url: str | None,
    diff: Comparison.Comparison,
    tags: PaginatedList.PaginatedList[Tag.Tag],
    repo_name: str,
) -> list[str]:
    output: list[str] = []
    header: list[str] = []
    tags_with_jira: list[str] = []
    tags_without_jira: list[str] = []
    if create_release_candidate:
        if release_url:
            header.append(
                f"Azure or github release run URL: <a class='external-link' href='{release_url}' rel='nofollow'>{release_url}</a>"
            )
    else:
        header.append(
            "This page is auto generated. Any manual modifications will be lost"
        )

    header.append(
        f"<h1 id='Currentreleasenotes{target_tag}-plannedreleasetotag{target_tag}'>{product_name} planned release to {target_environment} of tag {target_tag}</h1>",  # NOQA ES01
    )  # noqa: E501
    header.append(
        f"<h2 id='Currentreleasenotes{target_tag}-Changessincecurrentlyreleasedtag{current_tag}'>Changes since currently released tag {current_tag}</h2>",
    )  # noqa: E501

    for commit in diff.commits:
        tag_output = []
        found_jira = False
        release_tags = [tag.name for tag in tags if tag.commit.sha == commit.sha]
        if len(release_tags) == 0:
            release_tag = "can not find release tag"
        else:
            release_tag = release_tags[0]
        first_commit_line = commit.commit.message.splitlines()[0]
        match = re.search(r"(AEA[- ]\d*)", first_commit_line, re.IGNORECASE)
        if match:
            found_jira = True
            ticket_number = match.group(1).replace(" ", "-").upper()
            jira_link = f"https://nhsd-jira.digital.nhs.uk/browse/{ticket_number}"
            jira_details = get_jira_details(jira, ticket_number)
            if create_release_candidate:
                try:
                    logger.info(
                        f"Adding fix version {release_name} to ticket {ticket_number}"
                    )
                    fields = {"fixVersions": [{"add": {"name": str(release_name)}}]}
                    jira.edit_issue(
                        issue_id_or_key=ticket_number,
                        fields=fields,
                    )
                    logger.info(
                        f"Setting status of ticket {ticket_number} to Ready for Acceptance"
                    )
                    jira.issue_transition(
                        issue_key=ticket_number, status="Ready for Acceptance"
                    )
                except:  # noqa: E722
                    logger.error(traceback.format_exception(*sys.exc_info()))
                    logger.error(f"problem adding fix version for {ticket_number}")
        else:
            jira_details = JiraDetails("n/a", "n/a", [], "n/a", "n/a")
            found_jira = False
            jira_link = "n/a"
        user_story = jira_details.user_story.replace("\n", "\n<br/>")
        if release_tag == "can not find release tag":
            github_link = (
                f"https://github.com/NHSDigital/{repo_name}/commit/{commit.sha}"
            )
        else:
            github_link = (
                f"https://github.com/NHSDigital/{repo_name}/releases/tag/{release_tag}"
            )
        tag_output.append("<p>***")

        if jira_link == "n/a":
            tag_output.append(
                f"<br/>jira link               : {jira_link}"
            )  # noqa: E501
        else:
            tag_output.append(
                f"<br/>jira link               : <a class='external-link' href='{jira_link}' rel='nofollow'>{jira_link}</a>",
            )  # noqa: E501
        tag_output.append(
            f"<br/>jira title              : {escape(jira_details.jira_title)}"
        )
        tag_output.append(f"<br/>user story              : {escape(user_story)}")
        tag_output.append(f"<br/>commit title            : {escape(first_commit_line)}")
        tag_output.append(f"<br/>release tag             : {release_tag}")
        tag_output.append(
            f"<br/>github release          : <a class='external-link' href='{github_link}' rel='nofollow'>{github_link}</a>",
        )  # noqa: E501
        tag_output.append(f"<br/>Area affected           : {jira_details.components}")
        tag_output.append(
            f"<br/>Impact                  : {escape(jira_details.impact)}"
        )
        tag_output.append(
            f"<br/>Business/Service Impact : {escape(jira_details.business_service_impact)}"
        )
        tag_output.append("</p>")

        if create_release_candidate and found_jira:
            tags_with_jira = tags_with_jira + tag_output
        else:
            tags_without_jira = tags_without_jira + tag_output

    if create_release_candidate:
        tags_with_jira_header = ["<h3 id='jira_changes'>Changes with jira tickets</h3>"]
        tags_withouut_jira_header = [
            "<p>***</p>",
            "<h3 id='non_jira_changes'>Changes without jira tickets</h3>",
        ]
    else:
        tags_with_jira_header = []
        tags_withouut_jira_header = []
    output = (
        header
        + tags_with_jira_header
        + tags_with_jira
        + tags_withouut_jira_header
        + tags_without_jira
    )
    return output


def to_boolean(value) -> bool:
    valid = {
        "true": True,
        "t": True,
        "1": True,
        "false": False,
        "f": False,
        "0": False,
    }
    if isinstance(value, bool):
        return value

    if not isinstance(value, str):
        raise ValueError("invalid literal for boolean. Not a string.")

    lower_value = value.lower()
    if lower_value in valid:
        return valid[lower_value]
    else:
        raise ValueError('invalid literal for boolean: "%s"' % value)


def process_event(
    event: dict, jira: Jira, repo: Repository.Repository, confluence: Confluence
) -> None:
    current_tag = event["currentTag"]
    target_tag = event["targetTag"]
    repo_name = event["repoName"]
    target_environment = event["targetEnvironment"]
    product_name = event["productName"]
    release_notes_page_id = event["releaseNotesPageId"]
    release_notes_page_title = event["releaseNotesPageTitle"]
    create_release_candidate = to_boolean(event.get("createReleaseCandidate", "false"))
    release_prefix = event.get("releasePrefix")
    release_url = event.get("releaseURL")

    diff = repo.compare(base=current_tag, head=target_tag)
    tags = repo.get_tags()

    release_name = ""
    if create_release_candidate:
        release_name = f"{release_prefix}{target_tag}"
        logger.info(f"creating release {release_name} in JIRA")
        jira.add_version(
            project_key="AEA",
            project_id="15116",
            version=release_name,
        )
    output = create_release_notes(
        jira,
        current_tag,
        target_tag,
        target_environment,
        product_name,
        create_release_candidate,
        release_name,
        release_url,
        diff,
        tags,
        repo_name,
    )

    if create_release_candidate:
        logger.info(
            f"creating RC release notes page under page {release_notes_page_id}"
        )
        confluence.create_page(
            parent_id=release_notes_page_id,
            title=release_notes_page_title,
            body="\n".join(output),
            space="APIMC",
        )
    else:
        logger.info(f"updating release notes page {release_notes_page_id}")
        confluence.update_page(
            page_id=release_notes_page_id,
            title=release_notes_page_title,
            body="\n".join(output),
        )


# Enrich logging with contextual information from Lambda
@logger.inject_lambda_context()
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    try:
        logger.info(event)
        validate(event=event, schema=INPUT_SCHEMA)

        JIRA_TOKEN = os.getenv("JIRA_TOKEN")
        CONFLUENCE_TOKEN = os.getenv("CONFLUENCE_TOKEN")
        GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

        if JIRA_TOKEN is None:
            JIRA_TOKEN = str(parameters.get_secret("account-resources-jiraToken"))
        if CONFLUENCE_TOKEN is None:
            CONFLUENCE_TOKEN = str(
                parameters.get_secret("account-resources-confluenceToken")
            )

        jira = Jira(JIRA_URL, token=JIRA_TOKEN)
        confluence = Confluence(CONFLUENCE_URL, token=CONFLUENCE_TOKEN)
        github_auth = Auth.Token(str(GITHUB_TOKEN))
        gh = Github(auth=github_auth)
        repo_name = event["repoName"]
        repo = gh.get_repo(f"NHSDigital/{repo_name}")

        process_event(event=event, jira=jira, repo=repo, confluence=confluence)

        return {"status": "OK", "statusCode": 200}

    except SchemaValidationError as exception:
        # SchemaValidationError indicates where a data mismatch is
        logger.exception(exception)
        return {"body": str(exception), "statusCode": 400}
    except Exception as exception:
        logger.exception(exception)
        return {"body": str(exception), "statusCode": 500}
