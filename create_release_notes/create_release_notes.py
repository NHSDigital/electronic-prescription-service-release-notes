import os
import re
from atlassian import Jira, Confluence
from typing import Tuple
import traceback
import sys
from github import Github
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import SchemaValidationError, validate
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities import parameters

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
            "title": "The current tag",
            "examples": ["v1.0.104-beta"],
        },
        "targetTag": {
            "$id": "#/properties/targetTag",
            "type": "string",
            "title": "The target tag",
            "examples": ["v1.0.104-beta"],
        },
        "repoName": {
            "$id": "#/properties/repoName",
            "type": "string",
            "title": "The repo name",
            "examples": ["prescriptionsforpatients"],
        },
        "targetEnvironment": {
            "$id": "#/properties/targetEnvironment",
            "type": "string",
            "title": "The target environment",
            "examples": ["PROD"],
        },
        "productName": {
            "$id": "#/properties/productName",
            "type": "string",
            "title": "The product name",
            "examples": ["Prescriptions for Patients AWS layer"],
        },
        "releaseNotesPageId": {
            "$id": "#/properties/releaseNotesPageId",
            "type": "string",
            "title": "The release notes page id",
            "examples": ["693750029"],
        },
        "releaseNotesPageTitle": {
            "$id": "#/properties/releaseNotesPageTitle",
            "type": "string",
            "title": "The release notes page title",
            "examples": ["Current PfP AWS layer release notes - PROD"],
        },
        "createReleaseCandidate": {
            "$id": "#/properties/createReleaseCandidate",
            "type": "string",
            "title": "Whether to create a release candidate page",
            "examples": ["true"],
        },
        "releasePrefix": {
            "$id": "#/properties/releasePrefix",
            "type": "string",
            "title": "Prefix for the release in jira",
            "examples": ["Current PfP AWS layer release notes - PROD"],
        },
    },
}


def get_jira_details(
    jira: Jira, jira_ticket_number: str
) -> Tuple[str, str, str, str, str]:
    try:
        jira_ticket = jira.get_issue(jira_ticket_number)
        jira_title = jira_ticket["fields"]["summary"]
        jira_description = jira_ticket["fields"]["description"]
        components = [
            component["name"] for component in jira_ticket["fields"]["components"]
        ]
        match = match = re.search(
            r"(user story)(.*?)background",
            jira_description,
            re.IGNORECASE | re.MULTILINE | re.DOTALL,
        )
        if match:
            user_story = match.group(2).replace("*", "").replace("h3.", "").strip()
        else:
            user_story = "can not find user story"
        impact_field = jira_ticket.get("fields", {}).get("customfield_26905", {})
        if impact_field:
            impact = impact_field.get("value", "")
        else:
            impact = ""
        business_service_impact = jira_ticket["fields"].get("customfield_13618")
        return jira_title, user_story, components, impact, business_service_impact
    except:  # noqa: E722
        logger.error(traceback.format_exception(*sys.exc_info()))
        logger.error(f"problem getting details for {jira_ticket_number}")
        return f"can not find jira ticket for {jira_ticket_number}", "", "", "", ""


def create_release_notes(
    jira: Jira,
    current_tag: str,
    target_tag: str,
    repo_name: str,
    target_environment: str,
    product_name: str,
    create_release_candidate: str,
    release_name: str,
) -> str:
    gh = Github()
    repo = gh.get_repo(f"NHSDigital/{repo_name}")

    output = ["This page is auto generated. Any manual modifications will be lost"]
    output.append(
        f"<h1 id='Currentreleasenotes{target_tag}-plannedreleasetotag{target_tag}'>{product_name} planned release to {target_environment} of tag {target_tag}</h1>",  # NOQA ES01
    )  # noqa: E501
    output.append(
        f"<h2 id='Currentreleasenotes{target_tag}-Changessincecurrentlyreleasedtag{current_tag}'>Changes since currently released tag {current_tag}</h2>",
    )  # noqa: E501

    diff = repo.compare(base=current_tag, head=target_tag)
    tags = repo.get_tags()
    for commit in diff.commits:
        release_tags = [tag.name for tag in tags if tag.commit == commit]
        if len(release_tags) == 0:
            release_tag = "can not find release tag"
        else:
            release_tag = release_tags[0]
        first_commit_line = commit.commit.message.splitlines()[0]
        match = re.search(r"(AEA[- ]\d*)", first_commit_line, re.IGNORECASE)
        if match:
            ticket_number = match.group(1).replace(" ", "-").upper()
            jira_link = f"https://nhsd-jira.digital.nhs.uk/browse/{ticket_number}"
            (
                jira_title,
                user_story,
                components,
                impact,
                business_service_impact,
            ) = get_jira_details(jira, ticket_number)
            if create_release_candidate == "true":
                logger.info(
                    f"Adding fix version {release_name} to ticket {ticket_number}"
                )
                fields = {"fixVersions": [{"add": {"name": str(release_name)}}]}
                jira.edit_issue(
                    issue_id_or_key=ticket_number,
                    fields=fields,
                )
                logger.info(
                    f"Setting status of ticket {ticket_number} to Ready for test"
                )
                jira.issue_transition(issue_key=ticket_number, status="Ready for Test")
        else:
            jira_link = "n/a"
            jira_title = "n/a"
            user_story = "n/a"
            components = "n/a"
            impact = "n/a"
            business_service_impact = "n/a"
        user_story = user_story.replace("\n", "\n<br/>")
        github_link = (
            f"https://github.com/NHSDigital/{repo_name}/releases/tag/{release_tag}"
        )
        output.append("<p>***")

        if jira_link == "n/a":
            output.append(f"<br/>jira link               :  {jira_link}")  # noqa: E501
        else:
            output.append(
                f"<br/>jira link               :  <a class='external-link' href='{jira_link}' rel='nofollow'>{jira_link}</a>",
            )  # noqa: E501
        output.append(f"<br/>jira title              : {jira_title}")
        output.append(f"<br/>user story              : {user_story}")
        output.append(f"<br/>commit title            : {first_commit_line}")
        output.append(f"<br/>release tag             : {release_tag}")
        output.append(
            f"<br/>github release          : <a class='external-link' href='{github_link}' rel='nofollow'>{github_link}</a>",
        )  # noqa: E501
        output.append(f"<br/>Area affected           : {components}")
        output.append(f"<br/>Impact                  : {impact}")
        output.append(f"<br/>Business/Service Impact : {business_service_impact}")
        output.append("</p>")

    return "\n".join(output)


# Enrich logging with contextual information from Lambda
@logger.inject_lambda_context()
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    try:
        logger.info(event)
        validate(event=event, schema=INPUT_SCHEMA)
        current_tag = event["currentTag"]
        target_tag = event["targetTag"]
        repo_name = event["repoName"]
        target_environment = event["targetEnvironment"]
        product_name = event["productName"]
        release_notes_page_id = event["releaseNotesPageId"]
        release_notes_page_title = event["releaseNotesPageTitle"]
        create_release_candidate = event.get("createReleaseCandidate", "false")
        release_prefix = event.get("releasePrefix")

        JIRA_TOKEN = os.getenv("JIRA_TOKEN")
        CONFLUENCE_TOKEN = os.getenv("CONFLUENCE_TOKEN")

        if JIRA_TOKEN is None:
            JIRA_TOKEN = parameters.get_secret("account-resources-jiraToken")
        if CONFLUENCE_TOKEN is None:
            CONFLUENCE_TOKEN = parameters.get_secret(
                "account-resources-confluenceToken"
            )

        jira = Jira(JIRA_URL, token=JIRA_TOKEN)
        release_name = ""
        if create_release_candidate == "true":
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
            repo_name,
            target_environment,
            product_name,
            create_release_candidate,
            release_name,
        )
        confluence = Confluence(CONFLUENCE_URL, token=CONFLUENCE_TOKEN)
        if create_release_candidate == "true":
            logger.info("creating RC release notes page")
            confluence.create_page(
                parent_id=release_notes_page_id,
                title=release_notes_page_title,
                body=output,
                space="APIMC",
            )
        else:
            logger.info("updating release notes page")
            confluence.update_page(
                page_id=release_notes_page_id,
                body=output,
                title=release_notes_page_title,
            )
        return {"status": "OK", "statusCode": 200}
    except SchemaValidationError as exception:
        # SchemaValidationError indicates where a data mismatch is
        logger.exception(exception)
        return {"body": str(exception), "statusCode": 400}
    except Exception as exception:
        logger.exception(exception)
        return {"body": str(exception), "statusCode": 500}
