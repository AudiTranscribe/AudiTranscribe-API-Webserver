# IMPORTS
import datetime
import json

import semver
from flask import Flask, make_response, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from requests import get
from werkzeug.exceptions import HTTPException

# CONSTANTS
AUDITRANSCRIBE_REPO = "AudiTranscribe/AudiTranscribe"

# SETUP
# Set up flask application and limiter
application = Flask(__name__)
limiter = Limiter(
    application,
    key_func=get_remote_address,
    default_limits=["2/second", "1200/hour"]
)

# Get API server version from file
with open("API Server Version.txt", "r") as f:
    apiServerVersion = int(f.read())

# GLOBAL VARIABLES
cache = {}  # First element in tuple is the time of caching, second element is the data itself


# HELPER FUNCTIONS
def get_from_cache(key, cache_duration):
    """
    Helper function that attempts to get a value from the cache.
    """

    # Get current time
    now = round(datetime.datetime.now().timestamp())

    # Check if the cache contains the key and if the cache expired or not
    if key in cache and now <= cache[key][0] + cache_duration:
        return True, cache[key][1]

    # Invalid cache value
    return False, None


def add_to_cache(key, data):
    """
    Helper function that helps add data to the cache.
    """

    now = round(datetime.datetime.now().timestamp())
    cache[key] = (now, data)


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
@application.route("/get-raw-info")
def get_raw_info():
    # Try and get from the cache
    success, raw_info = get_from_cache("raw_info", 300)

    if not success:
        # Form the URL
        url = f"https://api.github.com/repos/{AUDITRANSCRIBE_REPO}/tags"

        # Send request to GitHub server for all the version tags
        response = get(url)

        if response.status_code == 200:
            # Save the response
            raw_info = response.text

            # Update the cache
            add_to_cache("raw_info", raw_info)
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
    raw_tag_info = get_json_from_response(get_raw_info())

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


@application.route("/check-if-have-new-version")
def check_if_have_new_version():
    """
    Checks if there is a new version that is newer than the current version.

    Note: this assumes that the version string is prefixed with a `v`.
    """

    # Get current version requested
    current_version = request.args.get("current-version", None)
    if current_version is None:
        return make_exception(
            code=400,
            name="Invalid Request",
            description="Did not include `current-version` with arguments."
        )

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

    try:
        newer_tag = str(semver.VersionInfo.parse(current_version[1:]))  # Tag must be at least the current version
    except ValueError as e:
        return make_exception(code=400, name="Invalid Request", description=str(e))

    if num_tags != 0:
        # Get the version tags
        versions = versions_json.get("versions")

        # Get latest newer tag in terms of semver version
        try:
            for i in range(num_tags):
                version = str(semver.VersionInfo.parse(versions[i][1:]))
                if semver.compare(newer_tag, version) == -1:  # Latest tag is smaller than the tag considered
                    newer_tag = versions[i][1:]
        except ValueError as e:
            return make_exception(code=400, name="Invalid Request", description=str(e))

    # Add the missing "v" in front of the version
    newer_tag = "v" + newer_tag

    # Check if there was a newer tag
    if newer_tag == current_version:
        return make_json("OK", 200, is_latest=True)
    else:
        return make_json("OK", 200, is_latest=False, newer_tag=newer_tag)


@application.route("/get-api-server-version")
def get_api_server_version():
    """
    Retrieves the API server version.
    """

    return make_json("OK", 200, api_server_version=apiServerVersion)


@application.route("/test-api-server-get")
@limiter.exempt()
def test_api_server_get():
    """
    Function that tests the API server returning protocol for GET requests.
    """

    # Check if the required parameters was sent along
    if request.args.get("is-testing", False) is not False:
        return make_json("OK", 200, data1="Hello World!", data2=False, data3=12.345, data4=678.9)
    else:
        return make_json("OK", 200, data1="Hello World!", data2=False, data3=12.345)


@application.route("/test-api-server-post", methods=["POST"])
@limiter.exempt()
def test_api_server_post():
    """
    Function that tests the API server returning protocol for POST requests.
    """

    if request.form.get("is-testing", False) is not False:
        return make_json("OK", 200, data1="Eggs and spam", data2=False, data3=12.345, data4=678.9)
    else:
        return make_json("OK", 200, data1="Eggs and spam", data2=False, data3=12.345)


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

    # Specially handle the "429 Too Many Requests" error
    if code == 429:
        return make_json("TOO MANY REQUESTS", 429, code=429, name=name, description=description)

    # Make and return the JSON response
    return make_json("ERROR", code, code=int(code), name=name, description=description)


@application.errorhandler(405)
def method_not_allowed_error_handler(_):
    return make_json(
        "METHOD NOT ALLOWED",
        405,
        code=405,
        name="Method Not Allowed",
        description=f"The '{request.method}' method is not allowed for the requested URL."
    )


# MAIN CODE
if __name__ == "__main__":
    application.run()
