"""
NOTICE:
- if you want change amount of data – change the COUNT constant
- the DB will be deleted, created and loaded automatically if you run script
- into your PyCharm or environment  set the env. variable
 DJANGO_SETTINGS_MODULE=library_project.settings
before running this script.
Example: export DJANGO_SETTINGS_MODULE=library_project.settings for terminal
on MAC OS. Search command for Windows if needed.
"""
import json
import random
from decimal import Decimal
from datetime import date, timedelta
import os
import subprocess

from faker import Faker
import django

django.setup()
from django.contrib.auth.hashers import make_password   # noqa: E402


fake = Faker()

DB_NAME = "db.sqlite3"

AUTHORS_COUNT = 25
BOOKS_COUNT = 5000
BORROWINGS_COUNT = 500
USERS_COUNT = 5

generated_data = []


def generate_authors(count: int = AUTHORS_COUNT) -> None:
    for pk in range(1, count + 1):
        generated_data.append(
            {
                "pk": pk,
                "model": "books_service.author",
                "fields": {
                    "first_name": fake.first_name(),
                    "last_name": fake.last_name(),
                    "author_profile_image": None
                },
            }
        )


def generate_books(count: int = BOOKS_COUNT) -> None:
    author_pk = 1
    for pk in range(1, count + 1):
        generated_data.append(
            {
                "pk": pk,
                "model": "books_service.book",
                "fields": {
                    "title": f"Book {pk}: part {random.randint(1, 5)}",
                    "title_image": None,
                    "author": author_pk,
                    "cover": random.choice(["hard", "soft"]),
                    "inventory": random.randint(0, 100),
                    "daily_fee": round(random.uniform(0, 100), 2),
                },
            }
        )
        author_pk += 1
        if author_pk == AUTHORS_COUNT + 1:
            author_pk = 1


def generate_borowing(count: int = BORROWINGS_COUNT) -> None:
    for pk in range(1, count + 1):
        borrow_date = date(2020, 10, 1) + timedelta(
            days=random.randint(1, 180)
        )
        expected_return_date = borrow_date + timedelta(
            days=random.randint(1, 180)
        )
        delta = expected_return_date - borrow_date
        actual_return_date = borrow_date + timedelta(
            days=random.randint(1, delta.days)
        )
        generated_data.append(
            {
                "pk": pk,
                "model": "borrowing_service.borrowing",
                "fields": {
                    "borrow_date": str(borrow_date),
                    "expected_return_date": str(expected_return_date),
                    "actual_return_date": random.choice(
                        (None, str(actual_return_date))
                    ),
                    "book": random.randint(1, BOOKS_COUNT),
                    "user": random.randint(1, USERS_COUNT),
                },
            }
        )


def generate_payments():
    max_digits = 8
    decimal_places = 2

    for pk in range(1, BORROWINGS_COUNT + 1):
        session_id = str(random.randint(10**8, 10**9 - 1))
        integer_part = random.randint(
            0, 10 ** (max_digits - decimal_places) - 1
        )
        decimal_part_int = random.randint(0, 99)
        random_value = Decimal(f"{integer_part}.{decimal_part_int:02}")
        payment_data = {
            "pk": pk,
            "model": "payments_service.payment",
            "fields": {
                "status": random.choice(("pending", "paid")),
                "type": random.choice(("payment", "fee")),
                "borrowing": pk,
                "session_url": fake.url(),
                "session_id": session_id,
                "money_to_pay": float(random_value),
            },
        }
        generated_data.append(payment_data)


def create_users() -> None:
    password = "GGduIU@"
    for pk in range(1, USERS_COUNT + 1):
        user_data = {
            "pk": pk,
            "model": "user.user",
            "fields": {
                "email": f"user{pk}@email.com",
                "password": make_password(password),
                "telegram_id": str(random.randint(10**8, 10**9 - 1)),
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "is_staff": True if pk == 1 else False,
                "is_superuser": True if pk == 1 else False
            },
        }

        generated_data.append(user_data)


def recreate_db_and_load_data(db_file_name: str = DB_NAME) -> None:
    if os.path.exists(db_file_name):
        os.remove(db_file_name)
        print(
            (
                f"DB {db_file_name} has been deleted. "
                f"Creating new one with generated data"
            )
        )
    mg_command = "python3 manage.py migrate"
    mg_result = subprocess.run(
        mg_command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    load_command = "python3 manage.py loaddata library_serice_data.json"
    load_result = subprocess.run(
        load_command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if mg_result.returncode == 0 and load_result == 0:
        print("Commands ran successfully")
    elif mg_result != 0:
        print(f"Command migrate notice: {mg_result.returncode}")
        print("Standard Output:")
        print(mg_result.stdout)
        print(mg_result.stderr)
    elif load_result != 0:
        print(f"Load command failed with an error: {load_result.returncode}")
        print("Standard Output:")
        print(load_result.stdout)
        print(load_result.stderr)


def caller():
    generate_authors()
    generate_books()
    create_users()
    generate_borowing()
    generate_payments()

    with open("library_serice_data.json", "w") as json_file:
        json.dump(generated_data, json_file, indent=4)

    recreate_db_and_load_data()


if __name__ == "__main__":
    caller()
