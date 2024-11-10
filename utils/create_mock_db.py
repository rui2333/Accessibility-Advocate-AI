import os
from datetime import datetime
from dataclasses import dataclass, asdict
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    insert,
)

# engine = create_engine("sqlite:///:memory:")
engine = create_engine("sqlite:///mock_programs.db")
metadata_obj = MetaData()

table_name = "mock_programs"
program_table = Table(
    table_name,
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("city", String(50), nullable=False),
    Column("state", String(20)),
    Column("program_name", String(100), nullable=False),
    Column("type", String(20), nullable=False),
)
metadata_obj.create_all(engine)

@dataclass
class Program():
    id: int
    city: str
    state: str
    program_name: str
    type: str

rows = [
    Program(1, "Boston", "MA", "The American Society for Deaf Children", "npo"),
    Program(2, "Boston", "MA", "Massachusetts Hands & Voices", "npo"),
    Program(3, "Boston", "MA", "Boston Children's hospital", "hospital"),
    Program(4, "San Francisco", "CA", "California Hands & Voices", "npo"),
    Program(5, "San Francisco", "CA", "Telehealth Options for Hearing Loss - CaptionCall", "commercial"),
    Program(6, "San Francisco", "CA", "California hearing center", "hospital"),
    Program(7, "Washington DC", "DC", "National Association of the Deaf.", "gov"),
]

for row in rows:
    stmt = insert(program_table).values(**asdict(row))
    with engine.begin() as connection:
        cursor = connection.execute(stmt)

"""
stmt = select(
    program_table.c.city,
    program_table.c.state,
    program_table.c.program_name,
    program_table.c.type,
).select_from(program_table)

with engine.connect() as connection:
    results = connection.execute(stmt).fetchall()
    print(results)
"""