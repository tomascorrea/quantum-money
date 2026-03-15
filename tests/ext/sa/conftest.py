# ruff: noqa: A003
"""Shared models and fixtures for SQLAlchemy extension tests."""

import pytest
from sqlalchemy import Column, Integer, create_engine
from sqlalchemy.orm import DeclarativeBase, Session

from quantum_money.ext.sa import MoneyType


class Base(DeclarativeBase):
    pass


class MoneyRawModel(Base):
    __tablename__ = "money_raw"
    id = Column(Integer, primary_key=True)
    amount = Column(MoneyType(representation="raw"))


class MoneyRealModel(Base):
    __tablename__ = "money_real"
    id = Column(Integer, primary_key=True)
    amount = Column(MoneyType(representation="real"))


class MoneyCentsModel(Base):
    __tablename__ = "money_cents"
    id = Column(Integer, primary_key=True)
    amount = Column(MoneyType(representation="cents"))


class MoneyCustomPrecisionModel(Base):
    __tablename__ = "money_custom_precision"
    id = Column(Integer, primary_key=True)
    amount = Column(MoneyType(representation="raw", precision=10, scale=2))


@pytest.fixture()
def engine():
    eng = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def session(engine):
    with Session(engine) as s:
        yield s
