# IMPORTS
from flask import Flask, make_response
from requests import get
import json
import semver

# SETUP
application = Flask(__name__)


# MAIN ROUTES
@application.route("/versions")
def versions():
    """Get a list of the version tags."""

    # Send request to GitHub server for all the version tags
    response = get("https://api.github.com/repos/AudiTranscribe/AudiTranscribe/tags")

    # Parse response text as JSON
    json_txt = json.loads(response.text)

    # Get version tags only and return
    return [entry["name"] for entry in json_txt]


@application.route("/latest-semver")
def latest_semver():
    """Get the latest version tag in terms of semver versioning."""

    # Get all version tags
    version_tags = versions()

    # Check if there are any version tags
    num_tags = len(version_tags)
    if num_tags == 0:
        return "Null"

    # Get latest tag in terms of semver version
    latest_tag = semver.VersionInfo.parse(version_tags[0][1:])
    for i in range(1, num_tags):
        curr_ver = semver.VersionInfo.parse(version_tags[i][1:])
        if semver.compare(str(latest_tag), str(curr_ver)) == -1:  # Latest tag is smaller than the current tag
            latest_tag = version_tags[i]

    # Make and return the response
    response = make_response(str(latest_tag), 200)
    response.mimetype = "text/plain"
    return response


@application.route("/latest-chrono")
def latest_chronologically():
    """Get the latest tag in chronological order."""

    version_tags = versions()
    response = make_response(version_tags[0] if len(version_tags) != 0 else "Null", 200)
    response.mimetype = "text/plain"
    return response


# MAIN CODE
if __name__ == "__main__":
    application.run()
