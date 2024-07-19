import re
import os
import csv
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

def extract_soup(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération de {url}: {e}")
        return None

def get_categories(url):
    soup = extract_soup(url)
    if not soup:
        return []
    
    categories = soup.find('ul', class_='nav nav-list').find_all('li')[1:]
    category_urls = [urljoin(url, category.find('a')['href']) for category in categories]
    return category_urls

def get_books_in_category(category_url):
    book_urls = []
    while category_url:
        soup = extract_soup(category_url)
        if not soup:
            break
        
        for article in soup.find_all('article', class_='product_pod'):
            book_url = urljoin(category_url, article.find('h3').find('a')['href'])
            book_urls.append(book_url)
        
        next_button = soup.find('li', class_='next')
        category_url = urljoin(category_url, next_button.find('a')['href']) if next_button else None
    
    return book_urls

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def download_image(image_url, category_name, image_name):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        if response.status_code == 200:
            category_folder = os.path.join("images", category_name)
            os.makedirs(category_folder, exist_ok=True)
            image_name = sanitize_filename(image_name)
            image_path = os.path.join(category_folder, image_name)
            with open(image_path, 'wb') as file:
                file.write(response.content)
        else:
            print(f"Échec du téléchargement de l'image depuis {image_url}")
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du téléchargement de l'image depuis {image_url}: {e}")

def extract_book_info(book_url):
    soup = extract_soup(book_url)
    if not soup:
        return {}
    
    book_info = {}
    book_info['title'] = soup.find('h1').text.strip()
    book_info['upc'] = soup.find('th', string='UPC').find_next('td').text.strip()
    book_info['price_incl_tax'] = soup.find('th', string='Price (incl. tax)').find_next('td').text.strip()[1:]
    book_info['price_excl_tax'] = soup.find('th', string='Price (excl. tax)').find_next('td').text.strip()[1:]
    book_info['availability'] = soup.find('th', string='Availability').find_next('td').text.strip()
    book_info['description'] = soup.find('meta', attrs={'name': 'description'})['content'].strip()
    book_info['category'] = soup.find('ul', class_='breadcrumb').find_all('li')[2].text.strip()
    book_info['rating'] = soup.find('p', class_='star-rating')['class'][1]
    image_url = soup.find('div', class_='item active').find('img')['src']
    parsed_uri = urlparse(book_url)
    domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
    absolute_image_url = urljoin(domain, image_url)
    image_name = f"{book_info['title']}.jpg"
    download_image(absolute_image_url, book_info['category'], image_name)
    book_info['image_url'] = absolute_image_url
    book_info['image_path'] = os.path.join("images", book_info['category'], image_name)
    
    return book_info

def write_to_csv(category_name, books):
    filename = f"{category_name}.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'upc', 'price_incl_tax', 'price_excl_tax', 'availability', 'description', 'category', 'rating', 'image_url', 'image_path']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(books)

def etl(url):
    categories = get_categories(url)
    for category_url in categories:
        print(f"Extraction de la catégorie: {category_url}")
        books = []
        book_urls = get_books_in_category(category_url)
        for book_url in book_urls:
            print(f"  Extraction du livre: {book_url}")
            book_info = extract_book_info(book_url)
            if book_info:
                books.append(book_info)
                print(book_info)
        category_name = category_url.rsplit('/', 2)[-2]
        write_to_csv(category_name, books)
