
from .CommonStockAPI import CCommonStockApi
from Common.CEnum import AUTYPE, DATA_FIELD, KL_TYPE
from Common.CTime import CTime
from Common.func_util import kltype_lt_day, str2float
from KLine.KLine_Unit import CKLine_Unit
from Orm import kline_repository
import datetime


def create_item_dict(data, column_name):
    for i in range(len(data)):
        data[i] = parse_time_column(data[i]) if i == 0 else str2float(data[i])
    return dict(zip(column_name, data))


def parse_time_column(inp):
    # 20210902113000000
    # 2021-09-13
    if len(inp) == 10:
        year = int(inp[:4])
        month = int(inp[5:7])
        day = int(inp[8:10])
        hour = minute = 0
    elif len(inp) == 17:
        year = int(inp[:4])
        month = int(inp[4:6])
        day = int(inp[6:8])
        hour = int(inp[8:10])
        minute = int(inp[10:12])
    elif len(inp) == 19:
        year = int(inp[:4])
        month = int(inp[5:7])
        day = int(inp[8:10])
        hour = int(inp[11:13])
        minute = int(inp[14:16])
    else:
        raise Exception(f"unknown time column from baostock:{inp}")
    return CTime(year, month, day, hour, minute)


def GetColumnNameFromFieldList(fileds: str):
    _dict = {
        "time": DATA_FIELD.FIELD_TIME,
        "date": DATA_FIELD.FIELD_TIME,
        "open": DATA_FIELD.FIELD_OPEN,
        "high": DATA_FIELD.FIELD_HIGH,
        "low": DATA_FIELD.FIELD_LOW,
        "close": DATA_FIELD.FIELD_CLOSE,
        "volume": DATA_FIELD.FIELD_VOLUME,
        "amount": DATA_FIELD.FIELD_TURNOVER,
        "turn": DATA_FIELD.FIELD_TURNRATE,
    }
    return [_dict[x] for x in fileds.split(",")]


class CHikyuuDatasource(CCommonStockApi):
    is_connect = None

    def __init__(self, code: str, k_type=KL_TYPE.K_DAY, begin_date=None, end_date=None, autype=AUTYPE.QFQ):
        super(CHikyuuDatasource, self).__init__(
            code, k_type, begin_date, end_date, autype)

    def get_kl_data(self):
        # 天级别以上才有详细交易信息
        # if kltype_lt_day(self.k_type):
        #     if not self.is_stock:
        #         raise Exception("没有获取到数据，注意指数是没有分钟级别数据的！")
        #     fields = "time,open,high,low,close"
        # else:
        #     fields = "date,open,high,low,close,volume,amount,turn"
        format_str = "%Y-%m-%d"
        dbname, code = self.find_dbname()
        start = datetime.datetime.strptime(
            self.begin_date, format_str).strftime("%Y%m%d0000")
        end = datetime.datetime.strptime(
            self.end_date, format_str).strftime("%Y%m%d0000")
        # 202312310000
        # autype_dict = {AUTYPE.QFQ: "2", AUTYPE.HFQ: "1", AUTYPE.NONE: "3"}
        ks = kline_repository.query_kline(
            code, dbname, start, end)
        result = []

        for i, v in enumerate(ks):
            pass
            # yield CKLine_Unit(create_item_dict(rs.get_row_data(), GetColumnNameFromFieldList(fields)))
        yield CKLine_Unit()
        # return result
        # if rs.error_code != '0':
        #     raise Exception(rs.error_msg)
        # while rs.error_code == '0' and rs.next():
        #     yield CKLine_Unit(create_item_dict(rs.get_row_data(), GetColumnNameFromFieldList(fields)))

    def SetBasciInfo(self):
        self.name = self.code
        self.is_stock = True

    def __convert_type(self):
        _dict = {
            KL_TYPE.K_DAY: 'd',
            KL_TYPE.K_WEEK: 'w',
            KL_TYPE.K_MON: 'm',
            KL_TYPE.K_5M: '5',
            KL_TYPE.K_15M: '15',
            KL_TYPE.K_30M: '30',
            KL_TYPE.K_60M: '60',
        }
        return _dict[self.k_type]

    def find_dbname(self):
        code = self.code.split(".")[1]
        db = ""
        if code.startswith("60"):
            db = "sh_"
        elif code.startswith("00"):
            db = "sz_"
        else:
            raise Exception(
                "cannot support kline data for market type:" + self.code
            )

        if self.k_type == KL_TYPE.K_DAY:
            db += "day"
        elif self.k_type == KL_TYPE.K_WEEK:
            db += "week"
        elif self.k_type == KL_TYPE.K_MON:
            db += "month"
        elif self.k_type == KL_TYPE.K_QUARTER:
            db += "quarter"
        elif self.k_type == KL_TYPE.K_YEAR:
            db += "year"

        return db, code
