import argparse
import os
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from . import selectors


def get_driver() -> webdriver.Chrome:
    """
    Get a Chrome webdriver.

    Returns:
        webdriver.Chrome: The webdriver.
    """

    driver = webdriver.Chrome()

    return driver


def get_url(page: int) -> str:
    """
    Get the URL for a page.

    Args:
        page (int): The page number.

    Returns:
        str: The URL for the page.
    """

    return f"https://www.joberty.mk/kompanii?page={page}&sort=review_number_desc"


def get_companies(driver: WebDriver) -> list[dict]:
    """
    Get the companies from the HTML.

    Args:
        html (str): The HTML.

    Returns:
        list[dict]: The companies.
    """

    companies = []

    cards = driver.find_elements(By.CSS_SELECTOR, selectors.card_selector)

    for card in cards:
        name = card.find_element(By.CSS_SELECTOR, selectors.name_selector)
        image = card.find_element(By.CSS_SELECTOR, selectors.image_selector)
        industry = card.find_element(By.CSS_SELECTOR, selectors.industry_selector)
        rating = card.find_element(By.CSS_SELECTOR, selectors.rating_selector)
        reviews = card.find_element(By.CSS_SELECTOR, selectors.reviews_selector)
        location = card.find_element(By.CSS_SELECTOR, selectors.location_selector)

        companies.append(
            {
                "name": name.text.strip() if name is not None else None,
                "image": image.get_attribute("src") if image is not None else None,
                "industry": industry.text.strip() if industry is not None else None,
                "rating": rating.text.strip() if rating is not None else None,
                "reviews": reviews.text.strip()[:-6] if reviews is not None else None,
                "location": location.text.strip() if location is not None else None,
            }
        )

    return companies


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: The parsed arguments.
    """

    parser = argparse.ArgumentParser(description="Scrape Joberty")

    parser.add_argument(
        "-n",
        type=int,
        default=300,
        help="How many companies to scrape (default: 300)",
    )

    return parser.parse_args()


def main() -> None:
    """
    Driver function.
    """

    args = parse_args()

    all_companies = []
    driver = get_driver()
    page = 1

    while True:
        print(f"Fetching page {page}...")
        driver.get(get_url(page))

        time.sleep(0.25)

        companies = get_companies(driver)
        print(f"Found {len(companies)} companies")

        all_companies.extend(companies)

        if len(companies) < 24:
            break

        page += 1

    print("Done")

    df = pd.DataFrame(
        data=all_companies,
        columns=["name", "image", "industry", "rating", "reviews", "location"],
    )
    os.makedirs("results", exist_ok=True)
    df.to_csv(os.path.join("results", "companies.csv"), index=False)

    df["name"].head(args.n).to_json(
        os.path.join("results", "discord.json"), force_ascii=False
    )


if __name__ == "__main__":
    main()
