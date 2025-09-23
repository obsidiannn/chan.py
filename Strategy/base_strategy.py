from . import strategy_enum, base_struct
import datetime
from Orm import models, kline_repository, strategy_record_repository


class BaseStrategy():
    start = 0
    end = 0
    predict = False
    date_label = None

    def strategy_enum(self) -> strategy_enum.StrategyEnum:
        raise Exception('strategy code must be provide!')

    def stock_filter(self, s: base_struct.Stock,
                     strategy_context: base_struct.StrategyContext) -> base_struct.ChooseEntity:
        # 主筛选分支
        raise Exception('没有声明主筛选逻辑')

    def get_date_label(self):
        date_label = datetime.datetime.strptime(
            self.end, "%Y-%m-%d").strftime("%Y%m%d")
        return date_label

    def strategy_calculate(self) -> base_struct.StrategyResult:
        # 遍历筛选器，内部调用stock_filter,返回 strategy_records, factor_result, strategy_record_property
        return None

    def is_realtime(self):
        return False

    def do_execute(self):
        # do strategy execute and save result to `stock_strategy_record`
        result = self.strategy_calculate()

        if len(result.strategy_records) > 0:
            strategy_record_repository.insert_many(
                self.get_date_label(), result.strategy_records, self.strategy_enum().code)


class BaseDailyStrategy(BaseStrategy):

    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.strategy_context = self.init_strategy_context()

    def get_future_end(self, need_future=True):
        # 返回可以用来作为计算依据的 index 终止位 ,none意味着最新的日期
        format_str = "%Y-%m-%d"
        start = datetime.datetime.strptime(
            self.start, format_str).strftime("%Y%m%d0000")
        end = datetime.datetime.strptime(
            self.end, format_str).strftime("%Y%m%d0000")
        # return start, end
        return self.start, self.end

    def init_strategy_context(self) -> base_struct.StrategyContext:
        a, b = self.get_future_end()
        context = base_struct.StrategyContext()
        context.start = a
        context.end = b
        return context

    def init_choosed_stock(self, data_index: str, choosed: base_struct.ChooseEntity):
        # 组装选中的stock 结果:
        industry = None
        total_reason = choosed.stock_reason
        total_point = choosed.point
        s = choosed.stock
        entity = models.StrategyRecord(
            market_code=s.market,
            stock_code=s.code,
            stock_name=s.name,
            strategy_code=self.strategy_enum().code,
            strategy_date=self.get_date_label(),
            industry_label=industry,
            is_retest=self.predict,
            concept_label='',
            total_point=total_point,
            data_index=data_index,
            total_reason=','.join(total_reason)
        )

        return entity

    def strategy_calculate(self) -> base_struct.StrategyResult:
        records = []
        factors = []
        record_properties = []
        stocks = kline_repository.query_all_stocks()

        for i in stocks:
            s = self.get_stock(i)
            # 不要双创板的
            if s.code[:2] == '30' or s.code[:2] == '68':
                continue
            # 不玩st
            if 'ST' in s.name:
                continue

            # data_index = strategy_code + strategy_date + stock_code + market
            strategy_type = self.strategy_enum()
            data_index = '%s-%s-%s-%s' % (
                strategy_type.code, self.get_date_label(), s.code, s.market
            )
            try:
                choosed = self.stock_filter(s, self.strategy_context)

                if choosed is not None:
                    record = self.init_choosed_stock(
                        data_index,
                        choosed)
                    records.append(record)
            except Exception as e:
                pass
        return base_struct.StrategyResult(records, factors, record_properties)

    def get_stock(self, item) -> base_struct.Stock:
        stock = base_struct.Stock()
        stock.code = item['code']
        stock.name = item['name']

        if stock.code[:2] == '00':
            stock.market = 'sz'
        if stock.code[:2] == '60':
            stock.market = 'sh'

        return stock
