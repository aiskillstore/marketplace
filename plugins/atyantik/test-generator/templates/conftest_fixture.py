"""Pytest fixtures for {test_module}."""

from __future__ import annotations

from collections.abc import Generator

import pytest


@pytest.fixture
def {fixture_name}() -> Generator[{ResourceType}, None, None]:
    """Provide {description} for tests.

    Yields:
        {ResourceType}: {Description of what is yielded}
    """
    # Setup
    resource = {ResourceType}()  # TODO: Initialize resource

    try:
        yield resource
    finally:
        # Teardown
        pass  # TODO: Add cleanup code
