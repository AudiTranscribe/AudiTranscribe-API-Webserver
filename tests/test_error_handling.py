"""
test_error_handling.py
Description: Tests for the error handling capabilities of the API server.

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
import application


# TESTS
def test_404_error(client):
    """Tests that a 404 error is shown for invalid URLs"""

    # The index page should return a 404 error
    response = client.get("/")
    json_data = response.json

    assert json_data["status"] == "ERROR"
    assert json_data["code"] == 404
    assert json_data["name"] == "Not Found"
    assert json_data["description"] == "The requested URL was not found on the server. If you entered the URL " \
                                       "manually please check your spelling and try again."

    # Invalid pages should always return a 404, regardless of the method
    response = client.patch("/a-non-existent-page")
    json_data = response.json

    assert json_data["status"] == "ERROR"
    assert json_data["code"] == 404
    assert json_data["name"] == "Not Found"
    assert json_data["description"] == "The requested URL was not found on the server. If you entered the URL " \
                                       "manually please check your spelling and try again."


def test_method_not_allowed(client):
    """Tests the server's response to invalid methods."""

    # A POST request to the "get API server version" page is not permitted
    response = client.post("/get-api-server-version")
    json_data = response.json

    assert json_data["status"] == "METHOD NOT ALLOWED"
    assert json_data["code"] == 405
    assert json_data["name"] == "Method Not Allowed"
    assert json_data["description"] == "The 'POST' method is not allowed for the requested URL."

    # A PUT request to the "get API server version" page is also not permitted
    response = client.put("/get-api-server-version")
    json_data = response.json

    assert json_data["status"] == "METHOD NOT ALLOWED"
    assert json_data["code"] == 405
    assert json_data["name"] == "Method Not Allowed"
    assert json_data["description"] == "The 'PUT' method is not allowed for the requested URL."


def test_too_many_requests_error(client):
    """Tests the flask rate limiter."""

    # First, force enabling of the rate limiter
    application.limiter.enabled = True

    try:
        # Now spam a page
        for _ in range(10):
            client.get("/get-api-server-version")
        response = client.get("/get-api-server-version")

        # Check the response
        json_data = response.json

        assert json_data["status"] == "TOO MANY REQUESTS"
        assert json_data["code"] == 429
        assert json_data["name"] == "Too Many Requests"
        assert json_data["description"] == "2 per 1 second"
    except Exception as e:
        raise e
    finally:
        # Disable limiter again
        application.limiter.enabled = False
