"""Erzeugt eine Beispiel-SQLite-Datenbank unter notebooks/public/data.db."""

import math
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "notebooks" / "public" / "data.db"


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    DB_PATH.unlink(missing_ok=True)

    rng = random.Random(42)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(
        """
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY,
            day TEXT NOT NULL,
            region TEXT NOT NULL,
            product TEXT NOT NULL,
            units INTEGER NOT NULL,
            revenue REAL NOT NULL
        );
        CREATE TABLE weather (
            day TEXT NOT NULL,
            city TEXT NOT NULL,
            temp_c REAL NOT NULL,
            rain_mm REAL NOT NULL
        );
        """
    )

    prices = {"Widget": 9.9, "Gadget": 24.5, "Doohickey": 4.2}
    regions = ["Nord", "Süd", "Ost", "West"]
    start = date(2025, 1, 1)

    sales = []
    for d in range(365):
        day = (start + timedelta(days=d)).isoformat()
        for region in regions:
            for product, price in prices.items():
                units = max(0, int(rng.gauss(20 + 10 * (d / 365), 6)))
                sales.append((day, region, product, units, round(units * price, 2)))
    conn.executemany(
        "INSERT INTO sales (day, region, product, units, revenue) VALUES (?, ?, ?, ?, ?)",
        sales,
    )

    cities = {"Zürich": 9.5, "Bern": 8.8, "Basel": 10.5, "Lugano": 12.5}
    weather = []
    for d in range(365):
        day = (start + timedelta(days=d)).isoformat()
        season = -8 * math.cos(2 * math.pi * d / 365)
        for city, base in cities.items():
            weather.append(
                (
                    day,
                    city,
                    round(base + season + rng.gauss(0, 2.5), 1),
                    round(max(0.0, rng.gauss(1.5, 4)), 1),
                )
            )
    conn.executemany("INSERT INTO weather VALUES (?, ?, ?, ?)", weather)

    conn.commit()
    conn.close()
    print(f"Datenbank geschrieben: {DB_PATH}")


if __name__ == "__main__":
    main()
