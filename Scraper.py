"""
Assignment 2 - Bookstore Intelligence Report
Collects book information from https://books.toscrape.com/
and performs competitor pricing and rating analysis.

Run: python scraper.py
Install: pip install requests beautifulsoup4 pandas matplotlib

PAGES = 3 for the required task, 5 for Bonus 1, or None for all pages.
"""

import re
import sys
import time
from urllib.parse import urljoin

import requests
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
PAGE_URL = BASE_URL + "catalogue/page-{}.html"

PAGES = None
BUDGET = 100.00
OUTPUT_CSV = "competitor_books.csv"

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


# ------------------------------------------------------------------
# Mission 1: Inspecting the structure of the bookstore website
# Product container : article.product_pod
# Book title        : h3 > a, stored in the title attribute
# Book price        : p.price_color
# Star rating       : p.star-rating (rating is another CSS class)
# Stock status      : p.availability
# Book URL          : relative link inside h3 > a
# ------------------------------------------------------------------

def get_soup(url):
    """Fetch a webpage and return its parsed HTML and final URL."""
    response = requests.get(url, timeout=15)

    if response.status_code == 404:
        return None

    response.raise_for_status()
    response.encoding = "utf-8"

    parsed_page = BeautifulSoup(response.text, "html.parser")
    return parsed_page, response.url


def parse_book(card, page_url):
    """Read the relevant details from a single book card."""
    anchor = card.select_one("h3 a")

    book_title = anchor["title"]
    book_url = urljoin(page_url, anchor["href"])

    raw_price = card.select_one(".price_color").get_text(strip=True)
    book_price = float(re.sub(r"[^\d.]", "", raw_price))

    rating_classes = card.select_one(".star-rating")["class"]
    rating_name = next(name for name in rating_classes
                       if name != "star-rating")
    book_rating = RATING_MAP[rating_name]

    stock_status = card.select_one(".availability").get_text(strip=True)

    book_info = {
        "Title": book_title,
        "Price": book_price,
        "Rating": book_rating,
        "Availability": stock_status,
        "URL": book_url
    }

    return book_info


def scrape_books(max_pages=None):
    """Collect book records from catalogue pages until the limit is reached."""
    all_books = []
    current_page = 1

    while max_pages is None or current_page <= max_pages:
        if current_page == 1:
            current_url = BASE_URL
        else:
            current_url = PAGE_URL.format(current_page)

        page_result = get_soup(current_url)

        if page_result is None:
            break

        soup, actual_url = page_result
        book_cards = soup.select("article.product_pod")

        if len(book_cards) == 0:
            break

        page_books = [
            parse_book(book_card, actual_url)
            for book_card in book_cards
        ]

        all_books.extend(page_books)

        print(
            f"Scraped page {current_page}: {len(book_cards)} books "
            f"(total {len(all_books)})"
        )

        current_page += 1
        time.sleep(0.3)

    return all_books


def best_basket(df, budget):
    """
    Find the basket with the highest combined star rating without exceeding
    the budget. If ratings tie, select the less expensive basket.

    Dynamic programming is used, with prices converted to pence.
    """
    budget_pence = round(budget * 100)

    products = []
    for index, (price, rating) in enumerate(
        zip(df["Price"], df["Rating"])
    ):
        cost = round(price * 100)

        if cost <= budget_pence:
            products.append((cost, rating, index))

    # Each state stores (rating total, negative cost, selected row indices).
    dp = [(0, 0, []) for _ in range(budget_pence + 1)]

    for cost, rating, index in products:
        for available in range(budget_pence, cost - 1, -1):
            previous_rating, negative_cost, selected = dp[available - cost]

            candidate = (
                previous_rating + rating,
                negative_cost - cost,
                selected + [index]
            )

            if candidate[:2] > dp[available][:2]:
                dp[available] = candidate

    maximum_rating, _, selected_rows = dp[budget_pence]

    selected_books = (
        df.iloc[selected_rows][["Title", "Price", "Rating"]]
        .reset_index(drop=True)
    )

    return selected_books, maximum_rating


def main():
    # Missions 2 and 3: Collect the data and create a DataFrame.
    books_df = pd.DataFrame(scrape_books(PAGES))

    print("\nFirst rows:")
    print(books_df.head())

    print("\nColumns:", list(books_df.columns), "| Rows:", len(books_df))
    print(books_df.dtypes)

    books_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"\nSaved {OUTPUT_CSV}")

    # Mission 4: Analyse prices, ratings, and stock availability.
    print("\n===== INTELLIGENCE ANALYSIS =====")

    highest_price_book = books_df.loc[books_df["Price"].idxmax()]
    print(
        f"1. Most expensive: {highest_price_book['Title']} "
        f"(£{highest_price_book['Price']:.2f})"
    )

    lowest_price_book = books_df.loc[books_df["Price"].idxmin()]
    print(
        f"2. Cheapest: {lowest_price_book['Title']} "
        f"(£{lowest_price_book['Price']:.2f})"
    )

    average_price = books_df["Price"].mean()
    print(f"3. Average price: £{average_price:.2f}")

    five_star_books = books_df[books_df["Rating"].eq(5)]
    print(f"4. Number of 5-star books: {len(five_star_books)}")

    stock_percentage = (
        books_df["Availability"]
        .str.contains("In stock", case=False)
        .mean() * 100
    )

    print(f"5. Percentage in stock: {stock_percentage:.1f}%")

    print("6. Top 5 highest-rated books (ties broken by lower price):")

    best_rated = books_df.sort_values(
        by=["Rating", "Price"],
        ascending=[False, True]
    ).head(5)

    print(best_rated[["Title", "Price", "Rating"]].to_string(index=False))

    cheapest_five_star = five_star_books.loc[
        five_star_books["Price"].idxmin()
    ]

    print(
        f"7. Cheapest 5-star book: {cheapest_five_star['Title']} "
        f"(£{cheapest_five_star['Price']:.2f})"
    )

    # Business decision evidence.
    print("\n===== BUSINESS DECISION EVIDENCE =====")

    rating_summary = (
        books_df.groupby("Rating")["Price"]
        .agg(["count", "mean"])
        .round(2)
    )

    print(rating_summary)

    print(
        f"5-star books average £{five_star_books['Price'].mean():.2f} "
        f"vs overall £{average_price:.2f}"
    )

    print(f"{stock_percentage:.1f}% of titles are in stock.")

    # CEO challenge: Select the best basket within the £100 budget.
    print(f"\n===== CEO CHALLENGE (budget £{BUDGET:.2f}) =====")

    chosen_books, rating_total = best_basket(books_df, BUDGET)

    print(chosen_books.to_string(index=False))
    print(f"Books chosen : {len(chosen_books)}")
    print(f"Total cost   : £{chosen_books['Price'].sum():.2f}")
    print(f"Total rating : {rating_total}")

    # Bonus tasks: Count ratings and produce a bar chart.
    rating_counts = books_df["Rating"].value_counts().sort_index()

    print("\nBooks per star rating:")
    print(rating_counts)

    chart = rating_counts.plot(
        kind="bar",
        color="steelblue",
        edgecolor="black"
    )

    chart.set_title("Number of Books by Star Rating")
    chart.set_xlabel("Star rating")
    chart.set_ylabel("Number of books")

    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig("rating_counts.png", dpi=150)
    plt.show()


class Tee:
    """Write console output to both the terminal and a report file."""

    def __init__(self, *streams):
        self.streams = streams

    def write(self, text):
        for stream in self.streams:
            stream.write(text)
            stream.flush()

    def flush(self):
        for stream in self.streams:
            stream.flush()


if __name__ == "__main__":
    with open("analysis_results.txt", "w", encoding="utf-8") as report:
        sys.stdout = Tee(sys.__stdout__, report)

        try:
            main()
        finally:
            sys.stdout = sys.__stdout__

    print("Analysis also saved to analysis_results.txt")
