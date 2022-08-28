"""
test_helpers.py
Description: Tests for the helper methods in the API server.

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
def test_cache_methods():
    """Tests the `get_from_cache` and `add_to_cache` methods."""

    # Try to get a non-existent key first
    success, value = application.get_from_cache("test", 1e10)  # Cache duration is 1e10
    assert success is False
    assert value is None

    # Now add to the cache
    application.add_to_cache("test", 123)

    # Try getting the key now
    success, value = application.get_from_cache("test", 1e10)
    assert success is True
    assert value == 123

    # Test whether the cache expiry is working
    success, value = application.get_from_cache("test", -1)  # Cache duration is -1 seconds
    assert success is False
    assert value is None
