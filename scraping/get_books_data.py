#################################################################################
#                                                                               #
#                             SCRIPT DE SCRAPING                                #
#                                                                               #
# Auteur: [Damien.GEY]                                                          #
# Date de Création: [17/07/24]                                                  #
# Description: Ce fichier contient les fonctions intermédiraire apeller avec la #
#              fonction principal etl du fichier main.py                        #
# Modules Importés:                                                             #
# - os: opérations sur le système de fichiers                                   #
# - csv: manipulation des fichiers CSV                                          #
# - typing: annotations de type                                                 #
# - urllib.parse: manipulation des URLs                                         #
# - scraping.utils: fonction utilitaires                                        #
#################################################################################
import os
import csv  
from typing import List, Dict, Union 
from urllib.parse import urljoin, urlparse
from scraping.utils import download_image, extract_soup

def get_categories(url: str) -> List[str]:
    """
    Récupère les URLs des catégories à partir de la page d'accueil du site.
    
    Args:
        url (str): L'URL de la page d'accueil du site.
    
    Returns:
        List[str]: Liste des URLs des catégories trouvées sur la page.
    """
    soup = extract_soup(url)  
    if not soup:  
        return [] 
    try:
        categories = soup.find('ul', class_='nav nav-list').find_all('li')[1:] 
        category_urls = [urljoin(url, category.find('a')['href']) for category in categories] 
        return category_urls  
    except AttributeError as e:  
        print(f"Erreur lors de la récupération des catégories depuis {url}: {e}") 
        return []  

def get_books_in_category(category_url: str) -> List[str]:
    """
    Récupère les URLs des livres dans une catégorie donnée.
    
    Args:
        category_url (str): L'URL de la catégorie à scraper.
    
    Returns:
        List[str]: Liste des URLs des livres trouvés dans la catégorie.
    """
    book_urls = []  
    while category_url:  
        soup = extract_soup(category_url)  
        if not soup:  
            break  
        
        try:
            for article in soup.find_all('article', class_='product_pod'):  
                book_url = urljoin(category_url, article.find('h3').find('a')['href'])  
                book_urls.append(book_url) 
        except AttributeError as e:  
            print(f"Erreur lors de la récupération des livres depuis {category_url}: {e}")  
            break  
        
        try:
            next_button = soup.find('li', class_='next')  
            category_url = urljoin(category_url, next_button.find('a')['href']) if next_button else None  
        except AttributeError as e:  
            print(f"Erreur lors de la récupération de la page suivante depuis {category_url}: {e}")  
            break 
    
    return book_urls

def extract_book_info(book_url: str) -> Dict[str, Union[str, float]]:
    """
    Extrait les informations d'un livre à partir de son URL.
    
    Args:
        book_url (str): L'URL du livre à scraper.
    
    Returns:
        Dict[str, Union[str, float]]: Dictionnaire contenant les informations extraites du livre.
    """
    soup = extract_soup(book_url)
    if not soup:
        return {} 
    book_info = {}
    try:
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
    except Exception as e:
        print(f"Erreur lors de l'extraction des informations du livre depuis {book_url}")
    return book_info

def write_to_csv(category_name: str, books: List[Dict[str, Union[str, float]]]) -> None:
    """ 
    Écrit les informations des livres dans un fichier CSV pour une catégorie donnée.
    
    Args:
        category_name (str): Nom de la catégorie pour laquelle écrire le fichier CSV.
        books (List[Dict[str, Union[str, float]]]): Liste des livres à écrire dans le fichier CSV.
    """
    filename = f"{category_name}.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'upc', 'price_incl_tax', 'price_excl_tax', 'availability', 'description', 'category', 'rating', 'image_url', 'image_path']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(books)