# Crawl4AI Skill Tests

This directory contains test scripts that verify the accuracy of all code examples in the SKILL.md file.

## Test Files

1. **test_basic_crawling.py** - Tests basic crawling setup with BrowserConfig and CrawlerRunConfig
2. **test_markdown_generation.py** - Tests markdown generation, fit_markdown, and content filters
3. **test_data_extraction.py** - Tests JSON/CSS extraction and LLM extraction strategies
4. **test_advanced_patterns.py** - Tests session management, proxies, and batch crawling

## Running Tests

### Run all tests

```bash
python run_all_tests.py
```

### Run individual tests

```bash
python test_basic_crawling.py
python test_markdown_generation.py
python test_data_extraction.py
python test_advanced_patterns.py
```

## Requirements

- Crawl4AI 0.7.4+
- All tests use example.com/example.org for testing
- LLM tests verify structure only (no API key required for basic validation)

## Test Coverage

✅ Basic crawling configuration
✅ Markdown generation and content filtering
✅ Schema-based data extraction
✅ Session management
✅ Proxy configuration structure
✅ Batch/concurrent crawling

## Notes

- Tests verify that SKILL.md examples are accurate and working
- All parameter names, imports, and API usage are cross-checked against actual Crawl4AI documentation
- Tests use live websites (example.com, example.org) for real-world validation
