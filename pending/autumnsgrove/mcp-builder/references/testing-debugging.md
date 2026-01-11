# MCP Testing and Debugging Guide

## Unit Testing Tools

### Basic Test Structure
```python
import pytest
from mcp.client import ClientSession
from mcp.client.stdio import stdio_client

@pytest.mark.asyncio
async def test_calculator_add():
    """Test calculator add tool"""
    async with stdio_client(
        command="python",
        args=["server.py"]
    ) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            assert any(t.name == "calculator_add" for t in tools.tools)

            # Call tool
            result = await session.call_tool(
                "calculator_add",
                {"a": 5, "b": 3}
            )

            assert result.content[0].text == "5 + 3 = 8"

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling"""
    async with stdio_client(
        command="python",
        args=["server.py"]
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Test with invalid arguments
            result = await session.call_tool(
                "calculator_add",
                {"a": "not a number", "b": 3}
            )

            assert result.isError == True
            assert "Invalid input" in result.content[0].text
```

### Testing Tool Handlers
```python
import pytest
from server import handle_calculator_add

@pytest.mark.asyncio
async def test_calculator_add():
    result = await handle_calculator_add({"a": 5, "b": 3})
    assert result[0].text == "5 + 3 = 8"

@pytest.mark.asyncio
async def test_calculator_add_negative():
    result = await handle_calculator_add({"a": -5, "b": 3})
    assert result[0].text == "-5 + 3 = -2"

@pytest.mark.asyncio
async def test_calculator_add_floats():
    result = await handle_calculator_add({"a": 1.5, "b": 2.5})
    assert result[0].text == "1.5 + 2.5 = 4.0"
```

### Integration Tests
```python
@pytest.mark.asyncio
async def test_full_tool_workflow():
    """Test complete MCP workflow"""
    async with stdio_client(
        command="python",
        args=["server.py"]
    ) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()

            # List tools
            tools_response = await session.list_tools()
            assert len(tools_response.tools) > 0

            # Call tool
            result = await session.call_tool(
                "calculator_add",
                {"a": 5, "b": 3}
            )
            assert not result.isError
            assert "8" in result.content[0].text
```

### Mocking External Dependencies
```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_api_call_with_mock():
    """Test API call with mocked HTTP request"""
    with patch('aiohttp.ClientSession.get') as mock_get:
        # Setup mock
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"key": "value"})
        mock_get.return_value.__aenter__.return_value = mock_response

        # Test
        result = await handle_api_call({"url": "https://api.example.com"})
        assert "value" in result[0].text
```

## Using MCP Inspector

### Installation
```bash
npm install -g @modelcontextprotocol/inspector
```

### Basic Usage
```bash
# Start inspector with your server
npx @modelcontextprotocol/inspector python server.py

# Inspector opens in browser at http://localhost:5173
```

### Testing with Inspector
```bash
# Test with specific tool call
npx @modelcontextprotocol/inspector python server.py \
  --tool calculator_add \
  --args '{"a": 5, "b": 3}'
```

### Inspector Features
- Interactive tool testing
- Real-time message inspection
- Schema validation
- Performance monitoring
- Request/response logging

## Logging Best Practices

### Logger Configuration
```python
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Use INFO in production
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler(sys.stderr)  # STDERR for stdio transport
    ]
)

logger = logging.getLogger(__name__)

# Log at appropriate levels
logger.debug("Detailed debugging information")
logger.info("General information about operations")
logger.warning("Something unexpected but handled")
logger.error("Error that needs attention")
logger.exception("Error with full traceback")
```

### Structured Logging
```python
async def call_tool(name: str, arguments: dict):
    try:
        return await execute_tool(name, arguments)
    except Exception as e:
        logger.error(
            f"Tool {name} failed",
            extra={
                "tool_name": name,
                "arguments": arguments,
                "error": str(e),
                "error_type": type(e).__name__
            },
            exc_info=True
        )
        raise
```

## Debugging Common Issues

### Issue 1: Server Not Starting
```python
# Add startup logging
async def main():
    logger.info("Starting MCP server...")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")

    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("STDIO transport initialized")
            await app.run(read_stream, write_stream, app.create_initialization_options())
    except Exception as e:
        logger.exception("Server startup failed")
        raise
```

### Issue 2: Tool Not Appearing
```python
# Debug tool registration
@app.list_tools()
async def list_tools():
    tools = [...]
    logger.info(f"Returning {len(tools)} tools: {[t.name for t in tools]}")
    return tools
```

### Issue 3: Arguments Not Received
```python
# Log received arguments
@app.call_tool()
async def call_tool(name: str, arguments: dict):
    logger.info(f"Tool called: {name}")
    logger.debug(f"Arguments received: {json.dumps(arguments, indent=2)}")
    logger.debug(f"Argument types: {[(k, type(v)) for k, v in arguments.items()]}")

    result = await execute_tool(name, arguments)
    logger.debug(f"Result: {result}")
    return result
```

### Issue 4: Resource Loading Errors
```python
@app.read_resource()
async def read_resource(uri: str):
    logger.info(f"Reading resource: {uri}")

    try:
        content = load_resource(uri)
        logger.debug(f"Loaded {len(content)} bytes")
        return content
    except FileNotFoundError:
        logger.error(f"Resource not found: {uri}")
        raise
    except Exception as e:
        logger.exception(f"Failed to load resource: {uri}")
        raise
```

## Performance Testing

### Measuring Tool Execution Time
```python
from datetime import datetime

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    start_time = datetime.now()
    logger.info(f"Tool call started: {name}")

    try:
        result = await execute_tool(name, arguments)
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Tool completed in {duration:.2f}s: {name}")
        return result
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(f"Tool failed after {duration:.2f}s: {name}")
        raise
```

### Load Testing
```python
import asyncio

async def load_test():
    """Test server under concurrent load"""
    async with stdio_client(
        command="python",
        args=["server.py"]
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Execute 100 concurrent tool calls
            tasks = [
                session.call_tool("calculator_add", {"a": i, "b": i})
                for i in range(100)
            ]

            start = datetime.now()
            results = await asyncio.gather(*tasks)
            duration = (datetime.now() - start).total_seconds()

            print(f"100 calls completed in {duration:.2f}s")
            print(f"Average: {duration/100:.4f}s per call")
```

## Test Organization

### Directory Structure
```
tests/
├── unit/
│   ├── test_tools.py
│   ├── test_resources.py
│   └── test_prompts.py
├── integration/
│   ├── test_server.py
│   └── test_workflows.py
└── fixtures/
    ├── sample_data.json
    └── test_config.py
```

### Pytest Configuration
```python
# conftest.py
import pytest
import asyncio

@pytest.fixture
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_server():
    """Start test server instance"""
    async with stdio_client(
        command="python",
        args=["server.py"]
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: MCP Server Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v --cov=src
```
