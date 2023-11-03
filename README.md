# ShoeX - Sneaker Profit Analytics 📊👟

Welcome to **ShoeX**! Your go-to Python tool for scraping sneaker data across various online retailers, analyzing the profits, and mastering the sneaker resale game.

![ShoeX Logo](path_to_logo_if_any.png)

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Scrapers](#scrapers)
- [Data Analysis](#data-analysis)
- [Contribution](#contribution)
- [License](#license)

## Features
- Multi-source scraping: Fetch sneaker data from leading retailers like Adidas, Nike, and more.
- Concurrent scraping: Uses multiprocessing for faster data extraction.
- Comprehensive analytics: Identify the most profitable sneakers for resale on StockX.
- Currency conversion: Seamlessly converts USD to PLN.
- Code quality assurance: Integrated with tools like `black`, `isort`, and `flake8`.

## Installation
To get started, ensure you have Python installed and then run:
```pip install -r requirements.txt```


## Usage
1. Clone the Repo:
    ```bash
    git clone https://github.com/yourusername/ShoeX.git
    ```
2. Navigate to the Directory:
    ```bash
    cd ShoeX
    ```
3. Run the Scraper:
    ```bash
    python src/main.py
    ```

## Scrapers
- **Adidas Scraper**: Extracts data from Adidas official site.
- **Nike Scraper**: Fetches latest sneaker listings from Nike.
- **EOBUWIE Scraper**: Dedicated scraper for eobuwie.pl.
- **StockX Scraper**: Grabs data specifically for resale insights on StockX.

## Data Analysis
Dive deep into the sneaker market with our `Analyzer` class:
- Convert sneaker prices between USD and PLN.
- Compute final prices after considering fees and taxes.
- Filter out sneakers based on profitability, demand, and volatility.

Check out `shoes_purchase_analyzer.py` for a detailed understanding.

## Contribution
Feel like adding a new scraper or enhancing the analytics? We welcome contributions! Just fork the repo, make your changes, and raise a PR.
