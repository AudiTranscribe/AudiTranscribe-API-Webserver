# TESTS
import application


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
