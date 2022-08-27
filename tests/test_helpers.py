import application


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
