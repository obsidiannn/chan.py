from . import models
from sqlalchemy import func


def insert_many(entities, date_label, ignore_check=False):
    if len(entities) <= 0:
        return
    try:
        result = models.session.add_all(
            entities
        )
        models.session.commit()
        return result
    finally:
        models.session.remove()


def query_empty_page(page=1, page_size=100):
    query = models.session.query(models.StrategyRecordProperty).filter(
        models.StrategyRecordProperty.close_5 is None
    ).order_by(models.StrategyRecordProperty.id.asc())
    return query.offset((page - 1) * page_size).limit(page_size).all()
