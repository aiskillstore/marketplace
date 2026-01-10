"""Tests for async {module_name}.{function_name}."""

from __future__ import annotations

import pytest
from {import_path} import {function_name}


class Test{FunctionNameCamelCase}:
    """Test cases for async {function_name}."""

    @pytest.mark.asyncio
    async def test_{function_name}_basic(self) -> None:
        """Test basic async functionality."""
        # Arrange
        # TODO: Set up test data

        # Act
        result = await {function_name}()

        # Assert
        assert result is not None

    @pytest.mark.asyncio
    async def test_{function_name}_concurrent(self) -> None:
        """Test concurrent execution."""
        # Arrange
        import asyncio

        # Act
        results = await asyncio.gather(
            {function_name}(),
            {function_name}(),
        )

        # Assert
        assert len(results) == 2
