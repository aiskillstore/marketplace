---
name: engineering-nba-data
description: Extracts, transforms, and analyzes NBA statistics using the nba_api Python library. Use when working with NBA player stats, team data, game logs, shot charts, league statistics, or any NBA-related data engineering tasks. Supports both stats.nba.com endpoints and static player/team lookups.
---

**Goal**: Extract and process NBA statistical data efficiently using the nba_api library for data analysis, reporting, and application development.

**IMPORTANT**: The nba_api library accesses stats.nba.com endpoints. All data requests return structured datasets that can be output as JSON, dictionaries, or pandas DataFrames.

## Workflow

### Phase 1: Setup and Installation

- Install nba_api: `pip install nba_api` if not yet installed
- Import required modules based on task:
  - `from nba_api.stats.endpoints import [endpoint_name]` for stats.nba.com data
  - `from nba_api.stats.static import players, teams` for static lookups
  - `from nba_api.stats.library.parameters import [parameter_classes]` for valid parameter values

### Phase 2: Data Retrieval

**For Player/Team Lookups (No API Calls)**:

- Use `players.find_players_by_full_name('player_name')` for player searches
- Use `teams.find_teams_by_full_name('team_name')` for team searches
- Both return dictionaries with `id`, `full_name`, and other metadata
- No HTTP requests are sent; data is embedded in the package

**For Stats Endpoints (API Calls)**:

- Identify the correct endpoint from [table of contents](docs/table_of_contents.md)
- Initialize endpoint with required parameters: `endpoint_class(param1=value1, param2=value2)`
- Access datasets using dot notation: `response_object.dataset_name`
- Retrieve data in desired format:
  - `.get_json()` for JSON string
  - `.get_dict()` for dictionary
  - `.get_data_frame()` for pandas DataFrame

**Custom Request Configuration**:

- Set custom headers: `endpoint_class(player_id=123, headers=custom_headers)`
- Set proxy: `endpoint_class(player_id=123, proxy='127.0.0.1:80')`
- Set timeout: `endpoint_class(player_id=123, timeout=100)` (in seconds)

### Phase 3: Data Processing

- Extract specific datasets from endpoint responses
- Transform data using pandas for aggregations, filtering, joins
- Normalize nested data structures as needed
- Handle multiple datasets returned by single endpoint

### Phase 4: Output and Storage

- Export to CSV: `df.to_csv('output.csv', index=False)`
- Export to JSON: Use `.get_json()` or `df.to_json()`
- Store in database using pandas `.to_sql()` method
- Cache responses to minimize API calls

## Rules

- **Required packages**: `nba_api` must be installed before use
- **Static first**: Always use static lookups (players/teams) for ID retrieval before making API calls
- **Parameter validation**: Reference [parameters.md](docs/nba_api/stats/library/parameters.md) for valid parameter values
- **Endpoint selection**: Check [table of contents](docs/table_of_contents.md) to find the correct endpoint
- **Rate limiting**: Be mindful of API rate limits; cache data when possible
- **Error handling**: Wrap API calls in try-except blocks to handle network failures
- **Data formats**: Know when to use JSON, dict, or DataFrame based on downstream requirements
- **Season format**: Seasons use format `YYYY-YY` (e.g., `2019-20`)
- **League IDs**: NBA=`00`, ABA=`01`, WNBA=`10`, G-League=`20`

## Acceptance Criteria

- Data retrieved successfully from appropriate endpoint or static source
- Correct parameters used based on documentation
- Data formatted appropriately for intended use case
- Error handling implemented for API failures
- Code follows Python best practices
- Results validated against expected structure
- Documentation references included where relevant

## Reference Documentation

**Quick access to common resources**:

- [Table of Contents](docs/table_of_contents.md) - Full documentation index
- [Examples](docs/nba_api/stats/examples.md) - Usage examples for endpoints and static data
- [Parameters](docs/nba_api/stats/library/parameters.md) - Valid parameter values and patterns
- [Endpoints Data Structure](docs/nba_api/stats/endpoints_data_structure.md) - Response format and methods
- [Players](docs/nba_api/stats/static/players.md) - Static player lookup functions
- [Teams](docs/nba_api/stats/static/teams.md) - Static team lookup functions
- [HTTP Library](docs/nba_api/library/http.md) - HTTP request details

**Endpoint-specific documentation**:

Refer to `docs/nba_api/stats/endpoints/[endpoint_name].md` for detailed parameter and dataset information for each endpoint.
