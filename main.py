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
