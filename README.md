# ShoeX - Sneaker Profit Analytics

## Description

ShoeX is a Python application designed to scrape sneaker data from various online retailers. The scraped data is transformed into a Pandas DataFrame, merged, and then analyzed to identify which sneakers are the most profitable to sell on StockX.

### Installation

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

## Code Quality Checks

This project uses several code quality checks including `black`, `isort`, `flake8`, `pylint`, and `mypy`. You can run all these checks using the Bash script included in the repository:

```bash
./run_checks.sh
```

## Usage

1. **Clone the Repo**: 
    ```bash
    git clone https://github.com/yourusername/ShoeX.git
    ```
  
2. **Navigate to the Directory**:
    ```bash
    cd ShoeX
    ```

3. **Run the Scraper**:
    ```bash
    python src/main.py
    ```
   This will generate a DataFrame with the scraped sneaker data.

### Main Script Structure

The main script (`main.py`) performs several tasks:

- Configures logging to `app.log`.
- Uses multiprocessing to run various scrapers concurrently.
- Merges the data into a single DataFrame.
- Analyzes the data to identify profitable sneakers for selling on StockX.

#### Logging Configuration

The logging is configured as follows:

- Filename: `app.log`
- Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- Date Format: `%d-%b-%y %H:%M:%S`

## Data Analysis

The `Analyzer` class is responsible for analyzing the merged DataFrame. It performs several key operations:

- **Currency Conversion**: It converts sneaker prices from USD to PLN using the current exchange rate from the NBP API, with a fallback to a hardcoded rate.
  
- **Price Formatting**: The class formats necessary columns and calculates a `finalPriceAfterTaxes` that takes into account various fees and taxes.
  
- **Profit Analysis**: Finally, the `Analyzer` filters the DataFrame to only include sneakers that have a significant price difference (`priceDiff > 50`), have some market demand (`numberOfBids > 0`), and are less volatile (`volatility < 1`).

### Configuration in Analyzer

- Transaction Fee: 9% (`0.09`)
- Payment Processing Fee: 3% (`0.03`)
- USD to PLN conversion: Fetched from NBP API or defaults to `4.0`
- Delivery Cost: USD 5.45

To understand more about how the analysis is performed, you can refer to the `Analyzer` class in the `shoes_purchase_analyzer.py` file.
