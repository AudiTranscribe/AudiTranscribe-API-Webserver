"""
test_main.py
Description: Tests for the main pages of the API server.

Copyright © 2022 AudiTranscribe Team

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

# IMPORTS
from io import BytesIO

import ujson


# TESTS
def test_get_raw_info(client):
    """Tests whether the server correctly returns raw info."""

    # First time is directly requesting from the GitHub API
    response = client.get("/get-raw-info")
    json_data = response.json
    assert json_data["status"] == "OK"

    # Find the release with tag "v0.1.2"
    raw_info = ujson.loads(json_data["raw_info"])
    required_release = None

    for release in raw_info:
        if release["name"] == "v0.1.2":
            required_release = release

    assert required_release is not None
    assert required_release["commit"]["sha"] == "716cbab35d290ec968f084d2243802f9ea7f018f"

    # Second time is from the cache
    response = client.get("/get-raw-info")
    json_data = response.json
    assert json_data["status"] == "OK"

    # Find the release with tag "v0.1.1"
    raw_info = ujson.loads(json_data["raw_info"])
    required_release = None

    for release in raw_info:
        if release["name"] == "v0.1.1":
            required_release = release

    assert required_release is not None
    assert required_release["commit"]["sha"] == "cbfd141de9e7c52299cc5116a6704ba7dd36f6f8"


def test_get_versions(client):
    """Tests the `get_versions` endpoint."""
    response = client.get("/versions")
    json_data = response.json

    assert json_data["status"] == "OK"
    assert json_data["count"] > 1
    assert "v0.1.2" in json_data["versions"]


def test_check_if_have_new_version(client):
    """Tests the endpoint that allows the client to check whether a new version is available."""

    # Test 1: Version 0.0.0 should say that version is not latest
    response = client.get("/check-if-have-new-version?current-version=v0.0.0")
    json_data = response.json

    assert json_data["status"] == "OK"
    assert json_data["is_latest"] is False

    # Test 2: Version 12.34.56 should say that the version is latest
    response = client.get("/check-if-have-new-version?current-version=v12.34.56")
    json_data = response.json

    assert json_data["status"] == "OK"
    assert json_data["is_latest"] is True

    # Test 3: Omitting the version should return an error
    response = client.get("/check-if-have-new-version")
    json_data = response.json

    assert json_data["status"] == "ERROR"
    assert json_data["code"] == 400
    assert json_data["name"] == "Invalid Request"
    assert json_data["description"] == "Did not include `current-version` with arguments."

    # Test 4: Invalid version format (without a v in the front) should return an error
    response = client.get("/check-if-have-new-version?current-version=alpha")
    json_data = response.json

    assert json_data["status"] == "ERROR"
    assert json_data["code"] == 400
    assert json_data["name"] == "Invalid Request"
    assert json_data["description"] == "Invalid semver format. Must start with a `v`."

    # Test 5: Invalid version format (with a v in the front but not valid semver) should return an error
    response = client.get("/check-if-have-new-version?current-version=v0.123")
    json_data = response.json

    assert json_data["status"] == "ERROR"
    assert json_data["code"] == 400
    assert json_data["name"] == "Invalid Request"
    assert json_data["description"] == "0.123 is not valid SemVer string"


def test_download_ffmpeg(client):
    """Tests the downloading of FFmpeg."""

    # Test 1: macOS without signature
    response = client.get("/download-ffmpeg?platform=macOS")

    with open("data/ffmpeg/ffmpeg-5.1.1-MACOS.zip", "rb") as f:
        actual_data = BytesIO(f.read())
        actual_data.seek(0)

    assert response.data == actual_data.read()

    # Test 2: macOS with signature
    response = client.get("/download-ffmpeg?platform=macOS&signature_needed=true")  # First time should load from file
    json_data = response.json

    assert json_data["status"] == "OK"
    assert json_data["signature"] == "9cd8808b50da3fcf434110572464db67f9ea3613b0731d27ce2eddddea3dfc14"

    # Test 3: Windows without signature
    response = client.get("/download-ffmpeg?platform=Windows")

    with open("data/ffmpeg/ffmpeg-5.1.1-WINDOWS.zip", "rb") as f:
        actual_data = BytesIO(f.read())
        actual_data.seek(0)

    assert response.data == actual_data.read()

    # Test 4: Windows with signature
    response = client.get("/download-ffmpeg?platform=Windows&signature_needed=true")  # Second time should be from cache
    json_data = response.json

    assert json_data["status"] == "OK"
    assert json_data["signature"] == "875086ba05f95e767c46362b08567c093f132f80d08c7d0ebd09f1b2f34dfc6f"

    # Test 5: Request without platform
    response = client.get("/download-ffmpeg")
    json_data = response.json

    assert json_data["status"] == "ERROR"
    assert json_data["code"] == 400
    assert json_data["name"] == "Invalid Request"
    assert json_data["description"] == "A platform must be specified."

    # Test 6: Request with invalid platform
    response = client.get("/download-ffmpeg?platform=nonexistent")
    json_data = response.json

    assert json_data["status"] == "ERROR"
    assert json_data["code"] == 400
    assert json_data["name"] == "Invalid Request"
    assert json_data["description"] == "Invalid platform 'NONEXISTENT'. Must be either 'MACOS' or 'WINDOWS'."

    # Test 7: Request with invalid `signature_needed` string
    response = client.get("/download-ffmpeg?platform=macos&signature_needed=maybe")
    json_data = response.json

    assert json_data["status"] == "ERROR"
    assert json_data["code"] == 400
    assert json_data["name"] == "Invalid Request"
    assert json_data["description"] == "Invalid signature option 'MAYBE'. Must be either 'TRUE' or 'FALSE'."


def test_download_audio_resource(client):
    """Tests the downloading of the audio resource."""

    response = client.get("/download-audio-resource")

    with open("data/audio/Breakfast.wav", "rb") as f:
        actual_data = BytesIO(f.read())
        actual_data.seek(0)

    assert response.data == actual_data.read()


def test_get_api_server_version(client):
    """Tests the API server version endpoint."""

    # Get the current API server version
    with open("API Server Version.txt", "r") as f:
        current_version = int(f.read())

    # Get the response from the server
    response = client.get("get-api-server-version")

    # Compare responses
    assert response.json == {"status": "OK", "api_server_version": current_version}


def test_api_server_get_and_post(client):
    """Tests the endpoints for the `api_server_get` and `api_server_post` pages."""

    # Test GET response
    response = client.get("/test-api-server-get")
    assert response.json == {"status": "OK", "data1": "Hello World!", "data2": False, "data3": 12.345}

    response = client.get("/test-api-server-get?is-testing=True")
    assert response.json == {"status": "OK", "data1": "Hello World!", "data2": False, "data3": 12.345, "data4": 678.9}

    # Test POST response
    response = client.post("/test-api-server-post")
    assert response.json == {"status": "OK", "data1": "Eggs and spam", "data2": False, "data3": 12.345}

    response = client.post("/test-api-server-post", data={"is-testing": True})
    assert response.json == {"status": "OK", "data1": "Eggs and spam", "data2": False, "data3": 12.345, "data4": 678.9}
