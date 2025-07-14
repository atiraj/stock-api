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
