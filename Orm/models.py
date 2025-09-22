# coding: utf-8
import configparser
import os
from typing import Any, Optional
import decimal

from sqlalchemy import (
    create_engine,
    BigInteger, Column, DECIMAL, Float, Index, Integer, String, Enum as SQLEnum,
    Table, Text
)
from sqlalchemy.dialects.mysql import BIT, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from sqlalchemy import BigInteger, DECIMAL, DateTime, Float, Index, Integer, String
from sqlalchemy.dialects.mysql import BIT, VARCHAR, ENUM
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

config = configparser.ConfigParser()
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
config.read(os.path.join(root_dir, 'config.ini'))  # 动态定位根目录配置文件

Base = declarative_base()
metadata = Base.metadata

# 创建引擎
engine = create_engine(
    "mysql+pymysql://root:888888@localhost:3308/hikyuu_analysis?charset=utf8mb4",
    max_overflow=0,
    pool_size=5,
    pool_timeout=10,
    pool_recycle=1,
    echo=True
)
# 绑定引擎
Session = sessionmaker(bind=engine, expire_on_commit=False)
session = scoped_session(Session)


class FactorResult(Base):
    __tablename__ = 'factor_result'
    __table_args__ = (
        Index('idx_factor_result', 'data_index',
              'factor_code', 'strategy_date'),
        {'comment': '因子结果记录表'}
    )

    id = Column(BigInteger, primary_key=True)
    data_index: Mapped[Optional[str]] = mapped_column(VARCHAR(64))
    strategy_date: Mapped[Optional[str]] = mapped_column(
        String(32, 'utf8mb4_general_ci'))
    factor_code: Mapped[Optional[str]] = mapped_column(VARCHAR(64))
    total_point: Mapped[Optional[int]] = mapped_column(Integer)
    reason: Mapped[Optional[str]] = mapped_column(VARCHAR(512))


class StrategyRecord(Base):
    __tablename__ = 'strategy_record'
    __table_args__ = (
        Index('idx_strategy_record', 'strategy_date', 'strategy_code',
              'stock_code', 'is_retest', 'data_index'),
        Index('uni_strategy_record', 'data_index', unique=True),
        {'comment': '策略记录表'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    strategy_date: Mapped[Optional[str]] = mapped_column(
        String(32, 'utf8mb4_general_ci'))
    strategy_code: Mapped[Optional[str]] = mapped_column(VARCHAR(32))
    stock_code: Mapped[Optional[str]] = mapped_column(VARCHAR(32))
    stock_name: Mapped[Optional[str]] = mapped_column(VARCHAR(32))
    market_code: Mapped[Optional[str]] = mapped_column(VARCHAR(4))
    industry_label: Mapped[Optional[str]] = mapped_column(
        String(32, 'utf8mb4_general_ci'))
    concept_label: Mapped[Optional[str]] = mapped_column(
        String(1024, 'utf8mb4_general_ci'))
    is_retest: Mapped[Optional[Any]] = mapped_column(BIT(1))
    total_point: Mapped[Optional[int]] = mapped_column(Integer)
    data_index: Mapped[Optional[str]] = mapped_column(
        String(255, 'utf8mb4_general_ci'))
    total_reason: Mapped[Optional[str]] = mapped_column(VARCHAR(1024))


class StrategyRecordProperty(Base):
    __tablename__ = 'strategy_record_property'
    __table_args__ = (
        Index('idx_strategy_record_property', 'data_index'),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    data_index: Mapped[str] = mapped_column(VARCHAR(255))
    limit_date: Mapped[Optional[str]] = mapped_column(VARCHAR(32))
    limit_start: Mapped[Optional[str]] = mapped_column(VARCHAR(32))
    raise_1: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(11, 2))
    raise_2: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(11, 2))
    raise_3: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(11, 2))
    raise_4: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(11, 2))
    raise_5: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(11, 2))
    max_raise_1: Mapped[Optional[decimal.Decimal]
                        ] = mapped_column(DECIMAL(11, 2))
    max_raise_2: Mapped[Optional[decimal.Decimal]
                        ] = mapped_column(DECIMAL(11, 2))
    max_raise_3: Mapped[Optional[decimal.Decimal]
                        ] = mapped_column(DECIMAL(11, 2))
    max_raise_4: Mapped[Optional[decimal.Decimal]
                        ] = mapped_column(DECIMAL(11, 2))
    max_raise_5: Mapped[Optional[decimal.Decimal]
                        ] = mapped_column(DECIMAL(11, 2))
    close_1: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(11, 2))
    close_2: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(11, 2))
    close_3: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(11, 2))
    close_4: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(11, 2))
    close_5: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(11, 2))
