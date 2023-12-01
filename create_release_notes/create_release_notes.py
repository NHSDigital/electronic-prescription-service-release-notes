import os
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
    "title": "Sample schema",
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
            "title": "The version to mark as released",
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
        jira.update_version(name=release_version, is_released=True)
    except SchemaValidationError as exception:
        # SchemaValidationError indicates where a data mismatch is
        logger.exception(exception)
        return {"body": str(exception), "statusCode": 400}
    except Exception as exception:
        logger.exception(exception)
        return {"body": str(exception), "statusCode": 500}
