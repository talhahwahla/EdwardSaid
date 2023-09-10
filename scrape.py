import json
import requests
from bs4 import BeautifulSoup
from langdetect import detect


def scrape_quotes_from_page(url):
    response = requests.get(url)

    if response.status_code == 200:
        html_content = response.text
    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
        exit()

    soup = BeautifulSoup(html_content, "html.parser")

    quotes_list = []

    quote_divs = soup.find_all("div", class_="quoteText")

    for div in quote_divs:
        quote_text = div.text.strip().split("\n")[0]

        author_name = div.find("span", class_="authorOrTitle").text.strip()

        book_element = div.find("a", class_="authorOrTitle")
        book_name = book_element.text.strip() if book_element else ""

        quote_info = {"quote": quote_text, "author": author_name, "book": book_name}
        quotes_list.append(quote_info)

    return quotes_list


def get_total_pages(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    pagination = soup.find("div", class_="u-textAlignRight")
    last_page = pagination.find_all("a")[-2].text.strip()
    return int(last_page)


def is_english(text):
    return detect(text) == "en"


base_url = "https://www.goodreads.com/author/quotes/16770310.Edward_W_Said"
total_pages = get_total_pages(base_url)

all_quotes = []
for page_number in range(1, total_pages + 1):
    page_url = f"{base_url}?page={page_number}"
    quotes_on_page = scrape_quotes_from_page(page_url)
    all_quotes.extend(quotes_on_page)

english_quotes = [quote for quote in all_quotes if is_english(quote["quote"])]
quotes_json = json.dumps(english_quotes, indent=2, ensure_ascii=False)

with open("quote.json", "w", encoding="utf-8") as json_file:
    json_file.write(quotes_json)
