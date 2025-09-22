from . import models
from sqlalchemy import func


def insert_many(date_label, entities=None, strategy_code=None):
    if len(entities) <= 0 or strategy_code == None:
        return
    print('策略:', strategy_code, 'date=', date_label, '结果录入')

    has_exist = models.session.query(
        func.count(models.StrategyRecord.id)
    ).filter(
        models.StrategyRecord.strategy_date == date_label,
        models.StrategyRecord.strategy_code == strategy_code
    ).scalar()
    if has_exist > 0:
        return

    try:
        result = models.session.add_all(
            entities
        )
        models.session.commit()
        return result
    finally:
        models.session.remove()


def update_many(entities):
    try:
        result = models.session.bulk_update_mappings(
            models.StrategyRecord, entities
        )
        models.session.commit()
        return result
    finally:
        models.session.remove()


def query_batch(date_label, strategy_code):
    return models.session.query(
        models.StrategyRecord
    ).filter(
        models.StrategyRecord.strategy_date == date_label,
        models.StrategyRecord.strategy_code == strategy_code
    ).order_by(
        models.StrategyRecord.total_point.desc()
    ).all()


def query_untest():
    return models.session.query(
        models.StrategyRecord
    ).filter(
        models.StrategyRecord.is_retest == False,
    ).all()


def query_batch_retest(strategy_code):
    return models.session.query(
        models.StrategyRecord
    ).filter(
        models.StrategyRecord.strategy_code == strategy_code,
        models.StrategyRecord.is_retest == True
    ).order_by(
        models.StrategyRecord.strategy_date.asc(),
    ).all()


def query_page(
        strategy_code,
        page=1,
        page_size=20,
) -> list[models.StrategyRecord]:
    """
    分页查询StrategyRecord，按id排序
    :param page: 页码，从1开始
    :param page_size: 每页条数
    :param order_desc: 是否倒序
    :return: 查询结果列表
    """
    query = models.session.query(models.StrategyRecord)
    query = query.filter(
        models.StrategyRecord.strategy_code == strategy_code,
    ).order_by(models.StrategyRecord.id.asc())
    return query.offset((page - 1) * page_size).limit(page_size).all()
