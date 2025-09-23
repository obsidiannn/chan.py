from . import strategy_enum
import decimal
from Orm import models


class Stock():
    code: str
    name: str
    market: str


class StrategyResult():
    def __init__(self, records, factors, record_properties) -> None:
        self.strategy_records = records
        self.factor_result = factors
        self.strategy_record_properties = record_properties

    '''
    strategy execute result structure
        1. strategy_record
        2. factor_result
        3. strategy_record_property
    '''
    strategy_records: list[models.StrategyRecord] = []
    strategy_record_properties: list[models.StrategyRecordProperty] = []


class ChooseEntity():
    def __init__(self, stock, reasons):
        self.stock_reason = reasons
        self.stock = stock

    stock: Stock
    stock_reason = []


class StrategyContext():
    start: str
    end: str
