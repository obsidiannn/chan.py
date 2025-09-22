from . import strategy_enum, base_struct
import datetime
from Orm import kline_repository

class BaseStrategy():
    # basic strategy class ,cannot directlly use , must implement by children strategy class
    '''
        因子负责提供相关的指标，数据
        具体的演算过程需要在子策略完成
        相当于子策略包含算子
    '''
    start = 0
    end = 0
    # 是否可回测 根据k线最新数据是否为最后数据确定
    predict = False
    date_label = None

    def strategy_enum(self) -> strategy_enum.StrategyEnum:
        raise Exception('strategy code must be provide!')

    def stock_filter(self, s: base_struct.Stock,
                     strategy_context: base_struct.StrategyContext) -> base_struct.ChooseEntity:
        # 主筛选分支
        raise Exception('没有声明主筛选逻辑')

    def get_date_label(self):
        return str(self.date_label)

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
        if len(result.factor_result) > 0:
            factor_result_repository.insert_many(
                result.factor_result, self.get_date_label())
        if len(result.strategy_record_properties) > 0:
            record_property_repository.insert_many(
                result.strategy_record_properties, self.get_date_label())


class BaseDaytimeStrategyV2(BaseStrategy):

    def __init__(self, sm, start, end, log_instance=None):
        self.start = start
        self.end = end
        self.total_amount = 0
        self.strategy_context = self.init_strategy_context()

    def get_future_end(self, need_future=True):
        # 返回可以用来作为计算依据的 index 终止位 ,none意味着最新的日期
        format_str = "%Y-%m-%d"
        start = datetime.datetime.strptime(
            self.start, format_str).strftime("%Y%m%d0000")
        end = datetime.datetime.strptime(
            self.end, format_str).strftime("%Y%m%d0000")
        return start, end

    def init_strategy_context(self) -> base_struct.StrategyContext:
        a, b = self.get_future_end()
        context = base_struct.StrategyContext()
        context.start = a
        context.end = b
        return context

    def init_choosed_stock(self, data_index: str, s: base_struct.Stock):
        # 组装选中的stock 结果:
        industry = None
        total_reason = []
        total_point = 0

        factor_results: list[models.FactorResult] = []
        record_properties: list[k_structs.RecordPropery] = []
        for f in factors_results:
            total_point += f.point
            factor_results.append(f.to_factor_result())
            total_reason.extend(f.reason)
            if len(f.properties) > 0:
                record_properties.extend(f.properties)

        entity = models.StrategyRecord(
            market_code=s.market,
            stock_code=s.code,
            stock_name=s.name,
            strategy_code=self.strategy_enum().code,
            strategy_date=self.get_date_label(),
            industry_label=industry,
            is_retest=self.predict,
            concept_label=','.join(concepts),
            total_point=total_point,
            data_index=data_index,
            total_reason=','.join(total_reason)
        )
        strategy_record_property = base_struct.convert_record_property(
            data_index, record_properties)

        return entity, factor_results, [strategy_record_property]

    def strategy_calculate(self) -> base_struct.StrategyResult:
        records = []
        factors = []
        record_properties = []
        stocks = kline_repository.query_all_stocks()

        for s in self.sm:
            # data_index = strategy_code + strategy_date + stock_code + market
            strategy_type = self.strategy_enum()
            data_index = '%s-%s-%s-%s' % (
                strategy_type.code, self.get_date_label(), s.code, s.market
            )

            choosed= self.stock_filter(s, factor_context)

            if choosed is not None:
                record, factor, properties = self.init_choosed_stock(
                    data_index,
                    s, choosed)
                records.append(record)

                if len(factor):
                    factors.extend(factor)
                if len(properties) > 0:
                    record_properties.extend(properties)

        return base_struct.StrategyResult(records, factors, record_properties)


