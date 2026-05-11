from sqlalchemy import Column, String, Integer, Float, Text, Index
from app.core.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    operating_flight_number = Column(String(20), nullable=False, index=True)
    segment = Column(String(20), nullable=False)
    cabin_class = Column(String(5), nullable=False)
    departure_airport = Column(String(10), nullable=False)
    arrival_airport = Column(String(10), nullable=False)
    destination_region = Column(String(100))
    nationality_code = Column(String(10))
    age_group = Column(String(20))
    meal_time = Column(String(30))
    customer_number = Column(String(128))
    segment_local_departure_datetime = Column(String(30))
    pre_booked_meal = Column(String(10), nullable=True)  # IATA SPML code, NULL = needs prediction

    __table_args__ = (
        Index("ix_customer_flight_date", "operating_flight_number", "segment_local_departure_datetime"),
    )


class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    segment = Column(String(20), nullable=False)
    segment_local_departure_date = Column(String(20), nullable=False)
    cabin_class = Column(String(5), nullable=False)
    meal_time = Column(String(30), nullable=False)
    meal_name = Column(Text)
    meal_pref = Column(String(30))

    __table_args__ = (
        Index("ix_meal_segment_date", "segment", "segment_local_departure_date"),
    )


class NationalityPref(Base):
    __tablename__ = "nationality_prefs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nationality_code = Column(String(10), nullable=False)
    day_of_week = Column(String(15), nullable=False)
    pork = Column(Float, default=0.0)
    chicken = Column(Float, default=0.0)
    beef = Column(Float, default=0.0)
    seafood = Column(Float, default=0.0)
    lamb = Column(Float, default=0.0)
    vegetarian = Column(Float, default=0.0)
    reasoning = Column(Text)
    sources = Column(Text)

    __table_args__ = (
        Index("ix_nat_pref_code_day", "nationality_code", "day_of_week"),
    )


class AgePref(Base):
    __tablename__ = "age_prefs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    age_group = Column(String(30), nullable=False, unique=True)
    pork = Column(Float, default=0.0)
    chicken = Column(Float, default=0.0)
    beef = Column(Float, default=0.0)
    seafood = Column(Float, default=0.0)
    lamb = Column(Float, default=0.0)
    vegetarian = Column(Float, default=0.0)
    reasoning = Column(Text)
    sources = Column(Text)


class DestinationPref(Base):
    __tablename__ = "destination_prefs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    airport_code = Column(String(10), nullable=False, unique=True)
    destination_region = Column(String(100), nullable=False)
    pork = Column(Float, default=0.0)
    chicken = Column(Float, default=0.0)
    beef = Column(Float, default=0.0)
    seafood = Column(Float, default=0.0)
    lamb = Column(Float, default=0.0)
    vegetarian = Column(Float, default=0.0)
    reasoning = Column(Text)
    sources = Column(Text)

    __table_args__ = (
        Index("ix_dest_region", "destination_region"),
    )


class MealtimePref(Base):
    __tablename__ = "mealtime_prefs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    meal_time = Column(String(30), nullable=False, unique=True)
    pork = Column(Float, default=0.0)
    chicken = Column(Float, default=0.0)
    beef = Column(Float, default=0.0)
    seafood = Column(Float, default=0.0)
    lamb = Column(Float, default=0.0)
    vegetarian = Column(Float, default=0.0)
    reasoning = Column(Text)


class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    segment = Column(String(20), nullable=False)
    segment_local_departure_date = Column(String(20), nullable=False)
    cabin_class = Column(String(5), nullable=False)
    meal_time = Column(String(30), nullable=False)
    protein_type = Column(String(30), nullable=False)
    original_meal_count = Column(Integer, default=0)

    __table_args__ = (
        Index(
            "ix_pred_history_segment_date",
            "segment", "segment_local_departure_date", "cabin_class", "meal_time",
        ),
    )
