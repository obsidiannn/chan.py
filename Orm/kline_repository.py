from . import models
from sqlalchemy import text


def query_kline(code, db_name, start, end):
    sql = 'select `date`, `open`, `high`, `low` , `close` ,`amount`, `count` from '
    sql += db_name + '.`' + code + '`'
    sql += 'where date between :start and :end '

    try:
        res_rows = models.session.execute(
            text(sql), {"start": start, "end": end}).fetchall()
        data = [dict(zip(result._fields, result)) for result in res_rows]
        return data
    except Exception as e:
        pass
    return []


def query_all_stocks():
    sql = 'select code,name  from hku_base '
    sql += 'where market_id in (1,2) and type = 1 and valid = 1'
    try:
        res_rows = models.session.execute(
            text(sql), {}).fetchall()
        return [dict(zip(result._fields, result)) for result in res_rows]
    except:
        pass
    return []
