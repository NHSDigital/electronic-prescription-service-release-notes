import os
from atlassian import Jira  # type: ignore
from typing import List
import traceback
import sys
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import SchemaValidationError, validate
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities import parameters

import requests

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
            "releaseTag": "v1.0.120-beta",
            "releasePrefix": "prescriptionsforpatients",
            "tickets": ["AEA-1234", "AEA-5678"],
        }
    ],
    "required": [
        "releaseTag",
        "releasePrefix",
        "tickets",
    ],
    "properties": {
        "releaseTag": {
            "$id": "#/properties/releaseTag",
            "type": "string",
            "title": "The release tag to create in confluence",
            "examples": ["v1.0.120-beta"],
        },
        "releasePrefix": {
            "$id": "#/properties/releasePrefix",
            "type": "string",
            "title": """
            <OPTIONAL> Prefix for the release in jira. The release created in jira has the format <releasePrefix><releaseTag>.
            Only used when createReleaseCandidate=true
            """,
            "examples": ["Clinical-Tracker-UI"],
        },
        "tickets": {
            "$id": "#/properties/tickets",
            "type": "array",
            "title": "List of jira tickets included in the release",
            "items": {
                "type": "string",
                "examples": ["AEA-1234", "AEA-5678"],
            },
        },
    },
}


def add_fix_version_to_jira(
    jira: Jira,
    release_name: str,
    tickets: List[str],
) -> list[str]:
    for ticket in tickets:
        try:
            ticket = ticket.strip("[]")  # Remove square brackets if present
            logger.info(f"Adding fix version {release_name} to ticket {ticket}")
            fields = {"fixVersions": [{"add": {"name": str(release_name)}}]}
            jira.edit_issue(
                issue_id_or_key=ticket,
                fields=fields,
            )
        except:  # noqa: E722
            logger.error(traceback.format_exception(*sys.exc_info()))
            logger.error(f"problem adding fix version for {ticket}")


def process_event(event: dict, jira: Jira) -> None:
    release_tag = event["releaseTag"]
    release_prefix = event.get("releasePrefix")
    tickets = event["tickets"]

    release_name = f"{release_prefix}-{release_tag}"
    try:
        logger.info(f"creating release {release_name} in JIRA")
        jira.add_version(
            project_key="AEA",
            project_id="15116",
            version=release_name,
        )
    except:  # noqa: E722
        logger.error(traceback.format_exception(*sys.exc_info()))
        logger.error(f"problem creating release {release_name} in JIRA")
    add_fix_version_to_jira(
        jira,
        release_name,
        tickets,
    )


# Enrich logging with contextual information from Lambda
@logger.inject_lambda_context()
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    try:
        logger.info(event)
        validate(event=event, schema=INPUT_SCHEMA)

        JIRA_TOKEN = os.getenv("JIRA_TOKEN")

        if JIRA_TOKEN is None:
            JIRA_TOKEN = str(parameters.get_secret("account-resources-jiraToken"))

        jira_session = requests.Session()
        jira = Jira(JIRA_URL, token=JIRA_TOKEN, session=jira_session)

        process_event(event=event, jira=jira)

        return {"status": "OK", "statusCode": 200}

    except SchemaValidationError as exception:
        # SchemaValidationError indicates where a data mismatch is
        logger.exception(exception)
        return {"body": str(exception), "statusCode": 400}
    except Exception as exception:
        logger.exception(exception)
        return {"body": str(exception), "statusCode": 500}
