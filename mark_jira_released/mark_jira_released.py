import os
from datetime import datetime
from atlassian import Jira
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import SchemaValidationError, validate
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities import parameters

JIRA_URL = "https://nhsd-jira.digital.nhs.uk/"
logger = Logger()

INPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft-07/schema",
    "$id": "https://example.com/example.json",
    "type": "object",
    "title": "root schema",
    "description": "The root schema comprises the entire JSON document.",
    "examples": [
        {
            "releaseVersion": "PfP-AWS-v1.0.243-beta",
        }
    ],
    "required": ["releaseVersion"],
    "properties": {
        "currentTag": {
            "$id": "#/properties/releaseVersion",
            "type": "string",
            "title": "The version in jira to mark as released",
            "examples": ["PfP-AWS-v1.0.243-beta"],
        },
    },
}


# Enrich logging with contextual information from Lambda
@logger.inject_lambda_context()
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    try:
        logger.info(event)
        validate(event=event, schema=INPUT_SCHEMA)
        release_version = event["releaseVersion"]

        JIRA_TOKEN = os.getenv("JIRA_TOKEN")

        if JIRA_TOKEN is None:
            JIRA_TOKEN = parameters.get_secret("account-resources-jiraToken")

        jira = Jira(JIRA_URL, token=JIRA_TOKEN)
        versions = jira.get_project_versions(key="AEA")
        release_versions = list(
            filter(lambda x: x.get("name") == release_version, versions)
        )
        if len(release_versions) != 1:
            # return 404 where no or more than 1 release version found
            message = f"can not find release version for {release_version}"
            logger.error(message)
            return {"statusCode": 404, "body": message}

        release_version_id = release_versions[0].get("id")
        logger.info(
            f"marking {release_version} with id {release_version_id} as released in Jira"
        )
        jira.update_version(
            version=release_version_id,
            is_released=True,
            release_date=datetime.today().strftime("%Y-%m-%d"),
        )
    except SchemaValidationError as exception:
        # SchemaValidationError indicates where a data mismatch is
        logger.exception(exception)
        return {"statusCode": 400, "body": str(exception)}
    except Exception as exception:
        logger.exception(exception)
        return {"statusCode": 500, "body": str(exception)}
