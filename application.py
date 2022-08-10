# IMPORTS
import json
import datetime

import semver
from flask import Flask, make_response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from requests import get
from werkzeug.exceptions import HTTPException

# CONSTANTS
AUDITRANSCRIBE_REPO = "AudiTranscribe/AudiTranscribe"

CACHE_DURATION = 300  # In seconds, so 300 means 5 minutes

# SETUP
application = Flask(__name__)
limiter = Limiter(
    application,
    key_func=get_remote_address,
    default_limits=["2/second"]
)

# GLOBAL VARIABLES
cache = {}  # First element in tuple is the time of expiry, second element is the data itself


# HELPER FUNCTIONS
def make_json(status, status_code, **kwargs):
    """
    Helper function that forms a JSON response based on the status string, status code, and additional arguments.
    """

    response = make_response(json.dumps({
        "status": status,
        **kwargs
    }), status_code)
    response.mimetype = "application/json"
    return response


def get_json_from_response(response):
    """
    Helper function that retrieves the JSON data from the response.
    """

    return response.json


# MAIN ROUTES
@application.route("/raw-tag-info")
def get_raw_tag_info():
    # Get current time
    now = round(datetime.datetime.now().timestamp())

    # Check if there is a cache and that the cache has yet to expire
    if "raw_tag_info" in cache and now <= cache["raw_tag_info"][0]:
        raw_info = cache["raw_tag_info"][1]
    else:
        # Form the URL
        url = f"https://api.github.com/repos/{AUDITRANSCRIBE_REPO}/tags"

        # Send request to GitHub server for all the version tags
        response = get(url)

        if response.status_code == 200:
            # Save the response
            raw_info = response.text

            # Update cache
            cache["raw_tag_info"] = (now + CACHE_DURATION, raw_info)
        else:
            return make_exception(
                code=response.status_code,
                name=response.reason,
                description="Could not fetch tags"
            )

    # Return as JSON
    return make_json("OK", 200, raw_info=raw_info)


@application.route("/versions")
def get_versions():
    """
    Get a list of the version tags.
    """

    # Get the raw tag info
    raw_tag_info = get_json_from_response(get_raw_tag_info())

    if raw_tag_info.get("status", "ERROR") == "OK":
        # Parse response text as JSON
        json_txt = json.loads(raw_tag_info.get("raw_info"))

        # Get version tags only and return
        return make_json("OK", 200, count=len(json_txt), versions=[entry["name"] for entry in json_txt])
    else:
        return make_exception(
            code=raw_tag_info.get("code", 500),
            name=raw_tag_info.get("name", "Fetch Error"),
            description=raw_tag_info.get("description")
        )


@application.route("/latest-semver")
def latest_semver():
    """
    Get the latest version tag in terms of semver versioning.
    """

    # Get all version tags
    versions_json = get_json_from_response(get_versions())

    # Check if fetched successfully
    if versions_json.get("status", "ERROR") == "ERROR":
        return make_exception(
            code=versions_json.get("code", 500),
            name=versions_json.get("name", "Fetch Error"),
            description=versions_json.get("description")
        )

    # Check if there are any version tags
    num_tags = versions_json.get("count", 0)
    latest_tag = None

    if num_tags != 0:
        # Get the version tags
        versions = versions_json.get("versions")

        # Get latest tag in terms of semver version
        latest_tag = str(semver.VersionInfo.parse(versions[0][1:]))

        for i in range(1, num_tags):
            curr_ver = str(semver.VersionInfo.parse(versions[i][1:]))
            if semver.compare(latest_tag, curr_ver) == -1:  # Latest tag is smaller than the current tag
                latest_tag = versions[i]  # We removed the "v" when parsing semver, so we add it back here

        # Add the missing "v" in front of the version
        latest_tag = "v" + latest_tag

    # Make and return the response
    return make_json("OK", 200, latest_semver=latest_tag)


@application.route("/latest-chrono")
def latest_chronologically():
    """
    Get the latest tag in chronological order.
    """

    # Get the version tags as JSON
    versions_json = get_json_from_response(get_versions())

    # Check if fetched successfully
    if versions_json.get("status", "ERROR") == "ERROR":
        return make_exception(
            code=versions_json.get("code", 500),
            name=versions_json.get("name", "Fetch Error"),
            description=versions_json.get("description")
        )

    # Try and get the latest tag
    latest_chrono = None
    if versions_json.get("count", 0) != 0:
        latest_chrono = versions_json["versions"][0]

    # Make and return the response
    return make_json("OK", 200, latest_chrono=latest_chrono)


# ERROR HANDLERS
@application.errorhandler(HTTPException)
def make_exception(e=None, code=None, name=None, description=None):
    """
    Return JSON instead of HTML for HTTP errors.
    """

    # Handle missing parameters
    if code is None:
        code = e.code

    if name is None:
        name = e.name

    if description is None:
        description = e.description

    # Make and return the JSON response
    return make_json("ERROR", code, code=int(code), name=name, description=description)


# MAIN CODE
if __name__ == "__main__":
    application.run()
