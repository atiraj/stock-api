# Develop FastAPI stock data API
_Exported on 7/14/2025 at 16:06:01 GMT+5:30 from Cursor (1.1.3)_

---

**User**

FastAPI Application Prompt: Stock Data API with Yahoo Finance
Goal: Develop a FastAPI application that provides two main endpoints: one to list all US stock symbols and another to retrieve detailed information for a given stock symbol, including historical prices and key financial metrics.

Technology Stack:

Backend Framework: FastAPI

Data Source: Yahoo Finance (via yfinance Python library)

Data Serialization: Pydantic

Requirement 1: Fetch all stock symbols in US exchange
Endpoint: /stocks/us_symbols

Method: GET

Description: This endpoint should return a list of common US stock symbols. Since Yahoo Finance itself doesn't offer a direct API to fetch all symbols for a given exchange, we'll need to leverage commonly available lists (e.g., S&P 500, NASDAQ 100, Dow Jones Industrial Average) or consider external, regularly updated sources if a truly comprehensive list is required. For this prompt, let's aim for a practical approach by providing a selection of widely traded US stocks.

Implementation Details:

Strategy: Utilize a curated list of major US indices (e.g., S&P 500, NASDAQ 100, Dow Jones) as a source for stock symbols. The yfinance library doesn't directly provide a function for all US symbols, so we'll simulate this by combining lists from well-known indices.

Response:

Success (200 OK): A JSON array of strings, where each string is a stock ticker symbol.

Example Response:

JSON

[
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "TSLA",
    // ... more symbols
]
Error Handling (Optional but Recommended):

Consider a 500 Internal Server Error if there's an issue fetching or compiling the symbol list.

Requirement 2: Given a stock symbol, fetch its start price, close price, 52-week high, 52-week low, PE ratio, and last six months' prices.
Endpoint: /stocks/{symbol}

Method: GET

Path Parameter:

symbol (string): The stock ticker symbol (e.g., AAPL, MSFT).

Description: This endpoint should retrieve and return comprehensive information for a specified stock symbol, including its current price data, 52-week performance, P/E ratio, and historical daily prices for the last six months.

Implementation Details:

Data Retrieval: Use the yfinance library's Ticker object to fetch data for the given symbol.

Metrics to Extract:

Start Price (Open Price for the current day): The opening price of the stock for the latest trading day.

Close Price (Current Close Price): The closing price of the stock for the latest trading day.

52-Week High: The highest price the stock reached in the past 52 weeks.

52-Week Low: The lowest price the stock reached in the past 52 weeks.

P/E Ratio: The Price-to-Earnings ratio.

Last Six Months' Prices: Daily closing prices for the past 6 months. This should be a list of objects, each containing a date and close_price.

Response:

Success (200 OK): A JSON object containing the requested stock data. Define a Pydantic model for this response.

Pydantic Model for Stock Details:

Python

from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class HistoricalPrice(BaseModel):
    date: date
    close_price: float

class StockDetails(BaseModel):
    symbol: str
    current_open_price: Optional[float]
    current_close_price: Optional[float]
    fifty_two_week_high: Optional[float]
    fifty_two_week_low: Optional[float]
    pe_ratio: Optional[float]
    last_six_months_prices: List[HistoricalPrice]
Example Response:

JSON

{
    "symbol": "AAPL",
    "current_open_price": 175.0,
    "current_close_price": 176.5,
    "fifty_two_week_high": 198.23,
    "fifty_two_week_low": 145.0,
    "pe_ratio": 29.5,
    "last_six_months_prices": [
        {"date": "2025-01-01", "close_price": 170.10},
        {"date": "2025-01-02", "close_price": 172.50},
        // ... more daily prices
        {"date": "2025-07-03", "close_price": 176.50}
    ]
}
Error Handling:

404 Not Found: If the symbol is invalid or data cannot be retrieved for it.

500 Internal Server Error: For unexpected errors during data fetching.

General Considerations for the FastAPI Application:
Asynchronous Operations: Leverage FastAPI's async def and await for I/O-bound operations (like fetching data from yfinance) to ensure non-blocking behavior.

Dependency Management: Use pipenv or poetry for managing dependencies (fastapi, uvicorn, yfinance, pandas).

Error Handling: Implement robust error handling with appropriate HTTP status codes and meaningful error messages.

Documentation: FastAPI automatically generates OpenAPI (Swagger UI) documentation. Ensure your endpoints are well-documented with descriptions, parameters, and response models.

Logging: Add basic logging to track requests and potential errors.

---

**Cursor**

```python
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime, timedelta
import yfinance as yf
import pandas as pd

app = FastAPI(title="US Stock Data API", description="Provides US stock symbols and detailed stock info via Yahoo Finance.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Curated list of major US stock symbols (S&P 500, NASDAQ 100, Dow Jones)
US_STOCK_SYMBOLS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "BRK-B", "JPM", "V", "UNH", "HD", "PG", "MA", "DIS", "BAC", "XOM", "VZ", "ADBE", "NFLX", "PFE", "KO", "CSCO", "PEP", "T", "INTC", "CMCSA", "ABT", "CRM", "WMT", "CVX", "MRK", "NKE", "MCD", "WFC", "COST", "DHR", "MDT", "TMO", "LLY", "NEE", "TXN", "LIN", "UNP", "HON", "ORCL", "AMGN", "QCOM", "ACN", "AVGO", "IBM", "SBUX", "LOW", "GS", "BLK", "CAT", "GE", "MMM", "AXP", "SPGI", "PLD", "CB", "USB", "RTX", "GILD", "ISRG", "ZTS", "SYK", "LMT", "DE", "DUK", "SO", "CL", "MO", "BKNG", "ADP", "CI", "TGT", "FISV", "EL", "CME", "APD", "BDX", "MMC", "ADI", "ITW", "SHW", "PNC", "EW", "AON", "ICE", "ETN", "NSC", "FDX", "GM", "F", "DAL", "UAL", "AAL"
    # ... add more as needed
]

class HistoricalPrice(BaseModel):
    date: date
    close_price: float

class StockDetails(BaseModel):
    symbol: str
    current_open_price: Optional[float]
    current_close_price: Optional[float]
    fifty_two_week_high: Optional[float]
    fifty_two_week_low: Optional[float]
    pe_ratio: Optional[float]
    last_six_months_prices: List[HistoricalPrice]

@app.get("/stocks/us_symbols", response_model=List[str], summary="List major US stock symbols", tags=["Stocks"])
async def get_us_stock_symbols():
    """Returns a curated list of major US stock ticker symbols."""
    try:
        logger.info("Fetching US stock symbols list.")
        return US_STOCK_SYMBOLS
    except Exception as e:
        logger.error(f"Error fetching US stock symbols: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch US stock symbols.")

@app.get("/stocks/{symbol}", response_model=StockDetails, summary="Get stock details by symbol", tags=["Stocks"])
async def get_stock_details(symbol: str):
    """Returns detailed stock info for a given symbol, including prices and key metrics."""
    try:
        logger.info(f"Fetching data for symbol: {symbol}")
        ticker = yf.Ticker(symbol)
        info = ticker.info
        if not info or 'regularMarketPrice' not in info:
            logger.warning(f"Symbol not found or no data: {symbol}")
            raise HTTPException(status_code=404, detail="Stock symbol not found or no data available.")

        # Get today's open/close
        hist_today = ticker.history(period="1d")
        current_open = hist_today['Open'].iloc[0] if not hist_today.empty else None
        current_close = hist_today['Close'].iloc[0] if not hist_today.empty else None

        # 52-week high/low
        fifty_two_week_high = info.get('fiftyTwoWeekHigh')
        fifty_two_week_low = info.get('fiftyTwoWeekLow')
        pe_ratio = info.get('trailingPE')

        # Last 6 months' daily close prices
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=182)
        hist_6mo = ticker.history(start=start_date, end=end_date)
        last_six_months_prices = [
            HistoricalPrice(date=idx.date(), close_price=row['Close'])
            for idx, row in hist_6mo.iterrows() if not pd.isna(row['Close'])
        ]

        return StockDetails(
            symbol=symbol.upper(),
            current_open_price=current_open,
            current_close_price=current_close,
            fifty_two_week_high=fifty_two_week_high,
            fifty_two_week_low=fifty_two_week_low,
            pe_ratio=pe_ratio,
            last_six_months_prices=last_six_months_prices
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stock details for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stock details.")

```

```pip-requirements
fastapi
uvicorn
yfinance
pandas

```

---

**User**

create virtual environment

---

**Cursor**

The virtual environment named `venv` has been created in your project directory. 

Next, you should activate the virtual environment and install the dependencies from `requirements.txt`. Would you like me to proceed with these steps? If so, please specify your shell (e.g., zsh, bash), or I can use the default for macOS (`zsh`).

---

**User**

pip install -r requirements.txt

---

**Cursor**

The virtual environment is now active, and all required dependencies (`fastapi`, `uvicorn`, `yfinance`, `pandas`, etc.) have been successfully installed.

You can now run your FastAPI application. Would you like to start the server with `uvicorn` (e.g., `uvicorn main:app --reload`), or do you have any other requests before launching the API?

---

**User**

launch the api

---

**Cursor**

The FastAPI application is now running with live reload enabled. 

You can access the API documentation and test the endpoints at:
- Swagger UI: http://127.0.0.1:8000/docs
- Redoc: http://127.0.0.1:8000/redoc

Let me know if you need help testing the endpoints, want to add features, or have any other requests!

---

**User**

stop the app

---

**Cursor**

To stop the FastAPI application running with uvicorn, simply press `CTRL+C` in the terminal where the server is running. This will gracefully shut down the server.

Would you like me to run any other commands or assist you with anything else?

---

**User**

can we change to get the stock symbol list from yfinance library rather than hard code

---

**Cursor**

Yes, you can fetch a list of US stock symbols dynamically using the yfinance library's screener functionality, rather than hardcoding them.

### How to do it

yfinance provides a `screen` function and `EquityQuery` class to query for stocks by region, exchange, etc. For example, to get a list of US stocks on the NASDAQ and NYSE:

```python
import yfinance as yf

# Get up to 250 US stocks (Yahoo's max per request)
symbols_df = yf.screen(
    yf.EquityQuery('and', [
        yf.EquityQuery('is-in', ['exchange', 'NMS', 'NYQ']),
        yf.EquityQuery('eq', ['region', 'us'])
    ]),
    count=250  # max allowed per request
)
symbols = symbols_df['symbol'].tolist()
```

- `"NMS"` = NASDAQ, `"NYQ"` = NYSE.
- You can adjust the `count` parameter (max 250 per request).
- For a truly comprehensive list, you would need to paginate through results (using the `offset` parameter).

### Next Steps

Would you like me to update your `/stocks/us_symbols` endpoint to fetch the list dynamically from yfinance using this approach? If so, should it return just the first 250, or do you want to implement pagination for a larger set?

```python
import yfinance as yf

# Get up to 250 US stocks (Yahoo's max per request)
symbols_df = yf.screen(
    yf.EquityQuery('and', [
        yf.EquityQuery('is-in', ['exchange', 'NMS', 'NYQ']),
        yf.EquityQuery('eq', ['region', 'us'])
    ]),
    count=250  # max allowed per request
)
symbols = symbols_df['symbol'].tolist()
```

---

**User**

implement pagination for larger set

---

**Cursor**

```python
# ... existing code ...
from fastapi import Query
# ... existing code ...
from yfinance import EquityQuery, screen
# ... existing code ...
@app.get("/stocks/us_symbols", response_model=List[str], summary="List major US stock symbols", tags=["Stocks"])
async def get_us_stock_symbols(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(100, ge=1, le=250, description="Number of symbols per page (max 250)")
):
    """Returns a paginated list of US stock ticker symbols from Yahoo Finance."""
    try:
        logger.info(f"Fetching US stock symbols list: page={page}, page_size={page_size}")
        offset = (page - 1) * page_size
        eq_query = EquityQuery('and', [
            EquityQuery('is-in', ['exchange', 'NMS', 'NYQ']),
            EquityQuery('eq', ['region', 'us'])
        ])
        result_df = screen(eq_query, offset=offset, count=page_size)
        if result_df is None or 'symbol' not in result_df:
            logger.warning("No symbols found from yfinance screener.")
            return []
        symbols = result_df['symbol'].tolist()
        return symbols
    except Exception as e:
        logger.error(f"Error fetching US stock symbols: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch US stock symbols.")
# ... existing code ...

```

```python
# ... existing code ...
@app.get("/stocks/us_symbols", response_model=List[str], summary="List major US stock symbols", tags=["Stocks"])
async def get_us_stock_symbols(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(100, ge=1, le=250, description="Number of symbols per page (max 250)")
):
    """Returns a paginated list of US stock ticker symbols from Yahoo Finance."""
    try:
        logger.info(f"Fetching US stock symbols list: page={page}, page_size={page_size}")
        offset = (page - 1) * page_size
        eq_query = EquityQuery('and', [
            EquityQuery('is-in', ('exchange', ('NMS', 'NYQ'))),
            EquityQuery('eq', ('region', 'us'))
        ])
        result_df = screen(eq_query, offset=offset, count=page_size)
        if result_df is None or 'symbol' not in result_df:
            logger.warning("No symbols found from yfinance screener.")
            return []
        symbols = result_df['symbol'].tolist()
        return symbols
    except Exception as e:
        logger.error(f"Error fetching US stock symbols: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch US stock symbols.")

# ... existing code ...
@app.get("/stocks/{symbol}", response_model=StockDetails, summary="Get stock details by symbol", tags=["Stocks"])
async def get_stock_details(symbol: str):
    """Returns detailed stock info for a given symbol, including prices and key metrics."""
    try:
        logger.info(f"Fetching data for symbol: {symbol}")
        ticker = yf.Ticker(symbol)
        info = ticker.info
        if not info or 'regularMarketPrice' not in info:
            logger.warning(f"Symbol not found or no data: {symbol}")
            raise HTTPException(status_code=404, detail="Stock symbol not found or no data available.")

        # Get today's open/close
        hist_today = ticker.history(period="1d")
        current_open = hist_today['Open'].iloc[0] if not hist_today.empty else None
        current_close = hist_today['Close'].iloc[0] if not hist_today.empty else None

        # 52-week high/low
        fifty_two_week_high = info.get('fiftyTwoWeekHigh')
        fifty_two_week_low = info.get('fiftyTwoWeekLow')
        pe_ratio = info.get('trailingPE')

        # Last 6 months' daily close prices
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=182)
        hist_6mo = ticker.history(start=start_date, end=end_date)
        last_six_months_prices = [
            HistoricalPrice(date=idx.to_pydatetime().date() if hasattr(idx, 'to_pydatetime') else idx.date(), close_price=float(row['Close']))
            for idx, row in hist_6mo.iterrows() if not pd.isna(row['Close'])
        ]

        return StockDetails(
            symbol=symbol.upper(),
            current_open_price=current_open,
            current_close_price=current_close,
            fifty_two_week_high=fifty_two_week_high,
            fifty_two_week_low=fifty_two_week_low,
            pe_ratio=pe_ratio,
            last_six_months_prices=last_six_months_prices
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stock details for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stock details.")
# ... existing code ...

```

```python
# ... existing code ...
        eq_query = EquityQuery('and', [
            EquityQuery('is-in', ('exchange', ('NMS', 'NYQ'))),
            EquityQuery('is-in', ('region', ('us',)))
        ])
# ... existing code ...
        last_six_months_prices = []
        for idx, row in hist_6mo.iterrows():
            close_val = row['Close']
            if pd.notna(close_val):
                # idx can be pd.Timestamp or datetime.date
                if hasattr(idx, 'to_pydatetime'):
                    dt = idx.to_pydatetime().date()
                elif hasattr(idx, 'date'):
                    dt = idx.date()
                else:
                    dt = idx
                last_six_months_prices.append(HistoricalPrice(date=dt, close_price=float(close_val)))
# ... existing code ...

```

```python
# ... existing code ...
        last_six_months_prices = []
        for idx, row in hist_6mo.iterrows():
            close_val = row['Close']
            if pd.notna(close_val):
                dt = None
                # idx can be pd.Timestamp, datetime, or date
                if hasattr(idx, 'to_pydatetime'):
                    dt = idx.to_pydatetime().date()
                elif hasattr(idx, 'date'):
                    dt_candidate = idx.date()
                    if isinstance(dt_candidate, date):
                        dt = dt_candidate
                elif isinstance(idx, date):
                    dt = idx
                if dt is not None:
                    last_six_months_prices.append(HistoricalPrice(date=dt, close_price=float(close_val)))
# ... existing code ...

```

```python
# ... existing code ...
import pandas as pd
from datetime import date, datetime
# ... existing code ...
        last_six_months_prices = []
        for idx, row in hist_6mo.iterrows():
            close_val = row['Close']
            if pd.notna(close_val):
                dt = None
                # idx can be pd.Timestamp, datetime, or date
                if isinstance(idx, pd.Timestamp):
                    dt = idx.date()
                elif isinstance(idx, datetime):
                    dt = idx.date()
                elif isinstance(idx, date):
                    dt = idx
                if dt is not None:
                    last_six_months_prices.append(HistoricalPrice(date=dt, close_price=float(close_val)))
# ... existing code ...

```

```python
# ... existing code ...
        last_six_months_prices = []
        for row in hist_6mo.itertuples():
            close_val = getattr(row, 'Close', None)
            if pd.notna(close_val):
                idx = getattr(row, 'Index', None)
                dt = None
                if isinstance(idx, pd.Timestamp):
                    dt = idx.date()
                elif isinstance(idx, datetime):
                    dt = idx.date()
                elif isinstance(idx, date):
                    dt = idx
                if dt is not None:
                    last_six_months_prices.append(HistoricalPrice(date=dt, close_price=float(close_val)))
# ... existing code ...

```

```python
# ... existing code ...
        last_six_months_prices = []
        for row in hist_6mo.itertuples():
            close_val = getattr(row, 'Close', None)
            idx = getattr(row, 'Index', None)
            dt = None
            if isinstance(idx, pd.Timestamp):
                dt = idx.date()
            elif isinstance(idx, datetime):
                dt = idx.date()
            elif isinstance(idx, date):
                dt = idx
            if close_val is not None and pd.notna(close_val) and dt is not None:
                last_six_months_prices.append(HistoricalPrice(date=dt, close_price=float(close_val)))
# ... existing code ...

```

The code is now updated to fetch US stock symbols dynamically from Yahoo Finance using yfinance's screener, with robust pagination support via `page` and `page_size` query parameters. The linter errors have been resolved, and the `/stocks/us_symbols` endpoint will now always return up-to-date results.

You can now restart your FastAPI app and test the endpoint, for example:
```
GET /stocks/us_symbols?page=1&page_size=100
```

Let me know if you want to test, further customize, or need help with anything else!

```plaintext
GET /stocks/us_symbols?page=1&page_size=100
```

---

**User**

please refactor the code i.e. put models in separate and api implementations in separate

---

**Cursor**

```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class HistoricalPrice(BaseModel):
    date: date
    close_price: float

class StockDetails(BaseModel):
    symbol: str
    current_open_price: Optional[float]
    current_close_price: Optional[float]
    fifty_two_week_high: Optional[float]
    fifty_two_week_low: Optional[float]
    pe_ratio: Optional[float]
    last_six_months_prices: List[HistoricalPrice]

```

```python
import logging
from fastapi import FastAPI, HTTPException, Query
from typing import List
from datetime import date, datetime, timedelta
import yfinance as yf
import pandas as pd
from yfinance import EquityQuery, screen
from models import HistoricalPrice, StockDetails

app = FastAPI(title="US Stock Data API", description="Provides US stock symbols and detailed stock info via Yahoo Finance.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/stocks/us_symbols", response_model=List[str], summary="List major US stock symbols", tags=["Stocks"])
async def get_us_stock_symbols(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(100, ge=1, le=250, description="Number of symbols per page (max 250)")
):
    """Returns a paginated list of US stock ticker symbols from Yahoo Finance."""
    try:
        logger.info(f"Fetching US stock symbols list: page={page}, page_size={page_size}")
        offset = (page - 1) * page_size
        eq_query = EquityQuery('and', [
            EquityQuery('is-in', ('exchange', ('NMS', 'NYQ'))),
            EquityQuery('is-in', ('region', ('us',)))
        ])
        result_df = screen(eq_query, offset=offset, count=page_size)
        if result_df is None or 'symbol' not in result_df:
            logger.warning("No symbols found from yfinance screener.")
            return []
        symbols = result_df['symbol'].tolist()
        return symbols
    except Exception as e:
        logger.error(f"Error fetching US stock symbols: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch US stock symbols.")

@app.get("/stocks/{symbol}", response_model=StockDetails, summary="Get stock details by symbol", tags=["Stocks"])
async def get_stock_details(symbol: str):
    """Returns detailed stock info for a given symbol, including prices and key metrics."""
    try:
        logger.info(f"Fetching data for symbol: {symbol}")
        ticker = yf.Ticker(symbol)
        info = ticker.info
        if not info or 'regularMarketPrice' not in info:
            logger.warning(f"Symbol not found or no data: {symbol}")
            raise HTTPException(status_code=404, detail="Stock symbol not found or no data available.")

        # Get today's open/close
        hist_today = ticker.history(period="1d")
        current_open = hist_today['Open'].iloc[0] if not hist_today.empty else None
        current_close = hist_today['Close'].iloc[0] if not hist_today.empty else None

        # 52-week high/low
        fifty_two_week_high = info.get('fiftyTwoWeekHigh')
        fifty_two_week_low = info.get('fiftyTwoWeekLow')
        pe_ratio = info.get('trailingPE')

        # Last 6 months' daily close prices
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=182)
        hist_6mo = ticker.history(start=start_date, end=end_date)
        last_six_months_prices = []
        for row in hist_6mo.itertuples():
            close_val = getattr(row, 'Close', None)
            idx = getattr(row, 'Index', None)
            dt = None
            if isinstance(idx, pd.Timestamp):
                dt = idx.date()
            elif isinstance(idx, datetime):
                dt = idx.date()
            elif isinstance(idx, date):
                dt = idx
            if close_val is not None and pd.notna(close_val) and dt is not None:
                last_six_months_prices.append(HistoricalPrice(date=dt, close_price=float(close_val)))

        return StockDetails(
            symbol=symbol.upper(),
            current_open_price=current_open,
            current_close_price=current_close,
            fifty_two_week_high=fifty_two_week_high,
            fifty_two_week_low=fifty_two_week_low,
            pe_ratio=pe_ratio,
            last_six_months_prices=last_six_months_prices
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stock details for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stock details.")

```

The codebase has been refactored:

- The Pydantic models (`HistoricalPrice` and `StockDetails`) are now defined in `models.py`.
- The FastAPI app and all API logic remain in `main.py`, which now imports the models from `models.py`.

This separation improves maintainability and clarity. You can now continue developing or testing your API with this cleaner structure.

Would you like to further modularize (e.g., move API routes to a separate file), or do you have any other requests?

