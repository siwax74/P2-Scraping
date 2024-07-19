from scraping.get_books_data import etl

if __name__ == "__main__":
    url = "https://books.toscrape.com/"
    etl(url)
