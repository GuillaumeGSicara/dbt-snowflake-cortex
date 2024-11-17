import json
import nltk  # type: ignore
import random

from typing import Any
from pathlib import Path
from datetime import datetime, timedelta
from constants import (
    TAGS,
    COUNTRIES,
    CAMPAIGNS,
    PRODUCTS,
)
from nltk.corpus import names  # type: ignore

# Download the names corpus if not already downloaded
nltk.download("names")

NB_CUSTOMERS = 2000


def generate_random_probability_distribution(
    n: int,
) -> list[float]:
    """
    Generate a random discrete probability distribution of size n
    """

    random_probabilities = [random.random() for _ in range(n)]
    total = sum(random_probabilities)
    return [p / total for p in random_probabilities]


def write_output_file(data: list, output_file: str):
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)


def generate_random_datetime(start_year: int, end_year: int) -> str:
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31, 23, 59, 59)
    delta = end_date - start_date
    random_seconds = random.randint(0, int(delta.total_seconds()))
    random_datetime = start_date + timedelta(seconds=random_seconds)
    return random_datetime.strftime("%Y-%m-%d %H:%M:%S")


def generate_customer_data() -> list[dict[str, Any]]:
    customer_data = []
    male_names = names.words("male.txt")
    female_names = names.words("female.txt")
    all_names = male_names + female_names

    for i in range(NB_CUSTOMERS):
        first_name: str = random.choice(all_names)
        last_name: str = random.choice(all_names)
        full_name = f"{first_name} {last_name}"
        customer_data.append(
            {
                "customer_id": i,
                "first_name": first_name,
                "last_name": last_name,
                "full_name": full_name,
                "email": f"{first_name.lower()}.{last_name.lower()}@example.com",
                "country": str(
                    random.choices(
                        population=COUNTRIES,
                        weights=generate_random_probability_distribution(
                            len(COUNTRIES)
                        ),
                    )[0]
                ),
            }
        )
    return customer_data


def generate_campaigns() -> list[dict[str, Any]]:
    campaign_data = []
    for i, campaign_name in enumerate(random.sample(CAMPAIGNS, len(CAMPAIGNS))):
        campaign_data.append(
            {
                "campaign_id": i,
                "name": campaign_name,
                "created_at": generate_random_datetime(2022, 2024),
                "tags": [tag for tag in TAGS if tag in campaign_name],
            }
        )
    return campaign_data


def generate_sends() -> list[dict[str, Any]]:
    send_data = []
    for customer_id in range(NB_CUSTOMERS):
        number_of_sends_received = random.choices(
            population=list(range(10)),
            weights=[
                0.2,  # 0
                0.5,  # 1
                0.15,  # 2
                0.1,  # 3
                0.05,  # 4
                0.020,  # 5
                0.015,  # 6
                0.005,  # 7
                0.0049,  # 8
                0.0001,  # 9
            ],
        )[0]
        for rand_number_of_sends in range(number_of_sends_received):
            send_data.append(
                {
                    "send_id": str(customer_id).zfill(9)
                    + str(rand_number_of_sends).zfill(9),
                    "customer_id": customer_id,
                    "campaign_id": random.randint(0, len(CAMPAIGNS) - 1),
                    "send_date": generate_random_datetime(2022, 2024),
                }
            )
    return send_data


def generate_sales() -> list[dict[str, Any]]:
    sales_data = []
    for customer_id in range(NB_CUSTOMERS):
        number_of_purchase = random.choices(
            population=list(range(5)),
            weights=[
                0.7,  # 0
                0.2,  # 1
                0.08,  # 2
                0.007,  # 3
                0.0003,  # 4
            ],
        )[0]
        for rand_number_of_purchase in range(number_of_purchase):
            sales_data.append(
                {
                    "purchase_id": str(customer_id).zfill(9)
                    + str(rand_number_of_purchase).zfill(9),
                    "customer_id": customer_id,
                    "product": random.choices(
                        PRODUCTS,
                        weights=generate_random_probability_distribution(len(PRODUCTS)),
                    )[0],
                    "purchased_at": generate_random_datetime(2022, 2024),
                }
            )
    return sales_data


if __name__ == "__main__":
    customer_data = generate_customer_data()
    write_output_file(
        customer_data,
        str(Path(__file__).parent / "data/raw_customers.json"),
    )

    campaign_data = generate_campaigns()
    write_output_file(
        campaign_data,
        str(Path(__file__).parent / "data/raw_campaigns.json"),
    )

    sends = generate_sends()
    write_output_file(
        sends,
        str(Path(__file__).parent / "data/raw_sends.json"),
    )

    sales = generate_sales()
    write_output_file(
        sales,
        str(Path(__file__).parent / "data/raw_sales.json"),
    )
