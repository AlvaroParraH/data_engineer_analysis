# Data Engineer Analysis

This repository contains a starter Playwright-based scraper example for collecting product information from Amazon.

## Overview

The project includes a simple script that opens a product or search page, waits for the page content to load, and extracts a title and price when available.

## Getting Started

1. Install the project dependencies with uv.
2. Create a local environment file based on [.env.example](.env.example).
3. Run the scraper from the project root.

## Usage

```bash
./.venv/bin/python scripts/amazon_scraper.py
```

You can also set a different Amazon URL before running:

```bash
AMAZON_PRODUCT_URL="https://www.amazon.com/dp/B08N5WRWNW" ./.venv/bin/python scripts/amazon_scraper.py
```

## Project Structure

- `scripts/` for scraper-related Python code
- `.env` for local environment variables
- `.env.example` as a template for configuration
