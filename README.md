Bookstore Data Intelligence: Python Scraper
This project was developed for Assignment 2 – Business Data and Text Mining. It uses Python to collect book information from Books to Scrape, organize the extracted information into a Pandas DataFrame, export the data to CSV, and perform basic business analysis.

Turn website information into structured data that can support business decisions.
Main Features
Extracts each book's title, price, star rating, stock status, and product page URL.
Automatically navigates through multiple catalogue pages using a reusable scraping function.
Translates written ratings (One, Two, Three, Four, Five) into numerical values from 1 to 5.
Removes currency symbols from prices and converts them into numeric values.
Exports the collected records to competitor_books.csv.
Calculates answers to seven business analysis questions.
Implements a knapsack-based solution to select books with the highest combined rating within a £100 budget.
Summarizes the distribution of star ratings and generates a bar chart.
Prerequisites
Make sure Python 3.8 or a newer version is installed, along with the following libraries:

requests
beautifulsoup4
pandas
matplotlib
Install the required packages using:


pip install requests beautifulsoup4 pandas matplotlib
Running the Program
Execute the following command from the project directory:


python scraper.py
The number of catalogue pages processed is determined by the PAGES setting in scraper.py.


Setting	Purpose
3	Complete the required task using the first three pages
5	Run Bonus 1 using five pages
None	Scrape all available catalogue pages
Generated Files
The program produces the following files:


Filename	Purpose
competitor_books.csv	Contains the collected book information
rating_counts.png	Visualizes the number of books at each rating level
Data Fields
The exported dataset contains these columns:


Column	Meaning	Sample value
Title	Complete title of the book	A Light in the Attic
Price	Book price in pounds sterling	51.77
Rating	Numerical star rating from 1 to 5	3
Availability	Indicates whether the book is in stock	In stock
URL	Direct link to the book's product page	https://books.toscrape.com/catalogue/...
Scraping and Analysis Process
Examine the website. The scraper identifies each product through its article.product_pod element. It retrieves the complete title from the link's title attribute, extracts the price from p.price_color, identifies the rating through the CSS classes of p.star-rating, and reads the availability status from p.availability.
Download catalogue pages. The requests library retrieves the HTML content. UTF-8 encoding is specified to ensure that currency symbols, such as £, display correctly.
Extract book details. BeautifulSoup processes each product card, while the parse_book() function collects the required fields into a dictionary.
Navigate through the catalogue. The scrape_books() function visits pages sequentially, collects the available records, and stops when the page limit is reached or no further catalogue pages are available.
Process and analyse the data. The collected records are converted into a Pandas DataFrame. The script then calculates the requested statistics, evaluates the £100 basket challenge, and creates a rating distribution chart.
Business Questions Covered
The script automatically calculates the following:

Which book has the highest price?
Which book has the lowest price?
What is the average price of all collected books?
How many books have a five-star rating?
What percentage of books are currently in stock?
Which five books have the highest ratings, with lower prices preferred when ratings are tied?
Which five-star book is the cheapest?
CEO Budget Challenge
The program also addresses the £100 purchasing challenge. A dynamic programming knapsack algorithm selects a combination of books that maximizes the total star rating without exceeding the available budget. If multiple baskets have the same total rating, the algorithm prefers the less expensive option.

The results include the selected books, their prices, the number of books purchased, the combined cost, and the overall rating score.

Repository Layout

.
├── scraper.py
├── competitor_books.csv
├── rating_counts.png
└── README.md
Additional Information
The scraper is designed for the Books to Scrape practice website.
A brief pause between page requests helps avoid sending requests too rapidly.
The analysis depends on the data collected during execution. Changing PAGES can affect the statistics, rating counts, and selected basket.
The script also saves its printed analysis to analysis_results.txt.

Author:
Kashaan Hayat
23i-5087
