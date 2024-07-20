#################################################################################
#                                                                               #
#                             SCRIPT DE SCRAPING                                #
#                                                                               #
# Auteur: [Damien.GEY]                                                          #
# Date de Création: [17/07/24]                                                  #
# Description: Ce script permet de scraper les informations des livres à partir #
#              d'un site web, incluant les catégories, les livres, les images   #
#              et les détails des livres, puis de sauvegarder ces informations  #
#              dans des fichiers CSV.                                           #
#                                                                               #
# Modules Importés:                                                             #
# - os: opérations sur le système de fichiers                                   #
# - re: expressions régulières                                                  #
# - csv: manipulation des fichiers CSV                                          #
# - typing: annotations de type                                                 #
# - requests: requêtes HTTP                                                     #
# - bs4 (BeautifulSoup): parsing HTML                                           #
# - urllib.parse: manipulation des URLs                                         #
#                                                                               #
#################################################################################
import os  
import re  
import csv  
from typing import List, Dict, Optional, Union 
from urllib.parse import urljoin, urlparse  
import requests  
from bs4 import BeautifulSoup


def extract_soup(url: str) -> Optional[BeautifulSoup]:
    """
    Extrait et retourne un objet BeautifulSoup à partir de l'URL donnée.
    
    Args:
        url (str): L'URL à partir de laquelle extraire le BeautifulSoup.
    
    Returns:
        Optional[BeautifulSoup]: Objet BeautifulSoup parsé à partir du contenu HTML de l'URL.
                                 Retourne None si une exception est levée lors de la requête.
    """
    try:
        response = requests.get(url)  # Effectue une requête GET vers l'URL donnée
        response.raise_for_status()  # Vérifie que la requête a réussi
        return BeautifulSoup(response.content, "html.parser")  # Retourne un objet BeautifulSoup parsé
    except requests.exceptions.RequestException as e:  # Capture les exceptions de requêtes HTTP
        print(f"Erreur lors de la récupération de {url}: {e}")  # Affiche un message d'erreur
        return None  # Retourne None en cas d'erreur

def get_categories(url: str) -> List[str]:
    """
    Récupère les URLs des catégories à partir de la page d'accueil du site.
    
    Args:
        url (str): L'URL de la page d'accueil du site.
    
    Returns:
        List[str]: Liste des URLs des catégories trouvées sur la page.
    """
    soup = extract_soup(url)  # Extrait le contenu HTML de la page d'accueil
    if not soup:  # Vérifie si le contenu HTML est vide
        return []  # Retourne une liste vide si le contenu est vide
    
    try:
        categories = soup.find('ul', class_='nav nav-list').find_all('li')[1:]  # Trouve les éléments de la liste de catégories
        category_urls = [urljoin(url, category.find('a')['href']) for category in categories]  # Construit les URLs des catégories
        return category_urls  # Retourne la liste des URLs des catégories
    except AttributeError as e:  # Capture les exceptions d'attributs manquants
        print(f"Erreur lors de la récupération des catégories depuis {url}: {e}")  # Affiche un message d'erreur
        return []  # Retourne une liste vide en cas d'erreur

def get_books_in_category(category_url: str) -> List[str]:
    """
    Récupère les URLs des livres dans une catégorie donnée.
    
    Args:
        category_url (str): L'URL de la catégorie à scraper.
    
    Returns:
        List[str]: Liste des URLs des livres trouvés dans la catégorie.
    """
    book_urls = []  # Initialise une liste pour les URLs des livres
    while category_url:  # Boucle tant que category_url n'est pas None
        soup = extract_soup(category_url)  # Extrait le contenu HTML de la page de la catégorie
        if not soup:  # Vérifie si le contenu HTML est vide
            break  # Sort de la boucle si le contenu est vide
        
        try:
            for article in soup.find_all('article', class_='product_pod'):  # Trouve tous les articles de livres
                book_url = urljoin(category_url, article.find('h3').find('a')['href'])  # Construit l'URL du livre
                book_urls.append(book_url)  # Ajoute l'URL du livre à la liste
        except AttributeError as e:  # Capture les exceptions d'attributs manquants
            print(f"Erreur lors de la récupération des livres depuis {category_url}: {e}")  # Affiche un message d'erreur
            break  # Sort de la boucle en cas d'erreur
        
        try:
            next_button = soup.find('li', class_='next')  # Trouve le bouton de pagination "next"
            category_url = urljoin(category_url, next_button.find('a')['href']) if next_button else None  # Met à jour l'URL de la page suivante
        except AttributeError as e:  # Capture les exceptions d'attributs manquants
            print(f"Erreur lors de la récupération de la page suivante depuis {category_url}: {e}")  # Affiche un message d'erreur
            break  # Sort de la boucle en cas d'erreur
    
    return book_urls  # Retourne la liste des URLs des livres

def sanitize_filename(filename: str) -> str:
    """
    Nettoie un nom de fichier en retirant les caractères non valides.
    
    Args:
        filename (str): Le nom de fichier à nettoyer.
    
    Returns:
        str: Le nom de fichier nettoyé.
    """
    return re.sub(r'[<>:"/\\|?*]', '', filename)  # Remplace les caractères non valides par une chaîne vide

def download_image(image_url: str, category_name: str, image_name: str) -> None:
    """
    Télécharge une image à partir d'une URL et la sauve dans un dossier spécifié.
    
    Args:
        image_url (str): L'URL de l'image à télécharger.
        category_name (str): Nom de la catégorie à laquelle appartient l'image.
        image_name (str): Nom de l'image à sauvegarder.
    """
    try:
        response = requests.get(image_url)  # Effectue une requête GET vers l'URL de l'image
        response.raise_for_status()  # Vérifie que la requête a réussi
        if response.status_code == 200:  # Vérifie si le code de statut est 200 (OK)
            category_folder = os.path.join("images", sanitize_filename(category_name))  # Construit le chemin du dossier de la catégorie
            os.makedirs(category_folder, exist_ok=True)  # Crée le dossier s'il n'existe pas déjà
            image_name = sanitize_filename(image_name)  # Nettoie le nom de l'image
            image_path = os.path.join(category_folder, image_name)  # Construit le chemin de l'image
            with open(image_path, 'wb') as file:  # Ouvre le fichier en mode binaire pour l'écriture
                file.write(response.content)  # Écrit le contenu de l'image dans le fichier
        else:
            print(f"Échec du téléchargement de l'image depuis {image_url}")  # Affiche un message d'erreur si le téléchargement échoue
    except requests.exceptions.RequestException as e:  # Capture les exceptions de requêtes HTTP
        print(f"Erreur lors du téléchargement de l'image depuis {image_url}: {e}")  # Affiche un message d'erreur

def extract_book_info(book_url: str) -> Dict[str, Union[str, float]]:
    """
    Extrait les informations d'un livre à partir de son URL.
    
    Args:
        book_url (str): L'URL du livre à scraper.
    
    Returns:
        Dict[str, Union[str, float]]: Dictionnaire contenant les informations extraites du livre.
    """
    soup = extract_soup(book_url)  # Extrait et parse le contenu HTML de l'URL du livre
    if not soup:
        return {}  # Retourne un dictionnaire vide si l'extraction échoue
    
    book_info = {}
    book_info['title'] = soup.find('h1').text.strip()  # Extrait le titre du livre
    book_info['upc'] = soup.find('th', string='UPC').find_next('td').text.strip()  # Extrait l'UPC du livre
    book_info['price_incl_tax'] = soup.find('th', string='Price (incl. tax)').find_next('td').text.strip()[1:]  # Extrait le prix TTC du livre
    book_info['price_excl_tax'] = soup.find('th', string='Price (excl. tax)').find_next('td').text.strip()[1:]  # Extrait le prix HT du livre
    book_info['availability'] = soup.find('th', string='Availability').find_next('td').text.strip()  # Extrait la disponibilité du livre
    book_info['description'] = soup.find('meta', attrs={'name': 'description'})['content'].strip()  # Extrait la description du livre
    book_info['category'] = soup.find('ul', class_='breadcrumb').find_all('li')[2].text.strip()  # Extrait la catégorie du livre
    book_info['rating'] = soup.find('p', class_='star-rating')['class'][1]  # Extrait la note du livre
    image_url = soup.find('div', class_='item active').find('img')['src']  # Extrait l'URL de l'image
    parsed_uri = urlparse(book_url)  # Parse l'URL du livre
    domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)  # Construit le domaine de l'URL
    absolute_image_url = urljoin(domain, image_url)  # Génère l'URL absolue de l'image
    image_name = f"{book_info['title']}.jpg"  # Génère le nom de l'image
    download_image(absolute_image_url, book_info['category'], image_name)  # Télécharge l'image
    book_info['image_url'] = absolute_image_url  # Ajoute l'URL de l'image aux informations du livre
    book_info['image_path'] = os.path.join("images", book_info['category'], image_name)  # Ajoute le chemin de l'image aux informations du livre
    
    return book_info  # Retourne le dictionnaire contenant les informations du livre

def write_to_csv(category_name: str, books: List[Dict[str, Union[str, float]]]) -> None:
    """ 
    Écrit les informations des livres dans un fichier CSV pour une catégorie donnée.
    
    Args:
        category_name (str): Nom de la catégorie pour laquelle écrire le fichier CSV.
        books (List[Dict[str, Union[str, float]]]): Liste des livres à écrire dans le fichier CSV.
    """
    filename = f"{category_name}.csv"  # Génère le nom du fichier CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:  # Ouvre le fichier CSV en mode écriture
        fieldnames = ['title', 'upc', 'price_incl_tax', 'price_excl_tax', 'availability', 'description', 'category', 'rating', 'image_url', 'image_path']  # Définit les en-têtes de colonnes
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)  # Crée un objet writer pour écrire dans le fichier CSV
        writer.writeheader()  # Écrit les en-têtes de colonnes
        writer.writerows(books)  # Écrit les informations des livres dans le fichier CSV

def etl(url):
    """
    Fonction principale qui effectue l'ETL (Extraction, Transformation, Load) pour le site de livres.
    
    Args:
        url (str): L'URL de la page d'accueil du site de livres.
    """
    categories = get_categories(url)  # Récupère les URLs des catégories
    for category_url in categories:
        print(f"Extraction de la catégorie: {category_url}")  # Affiche un message d'extraction de catégorie
        books = []
        book_urls = get_books_in_category(category_url)  # Récupère les URLs des livres dans la catégorie
        for book_url in book_urls:
            print(f"  Extraction du livre: {book_url}")  # Affiche un message d'extraction de livre
            book_info = extract_book_info(book_url)  # Extrait les informations du livre
            if book_info:
                books.append(book_info)  # Ajoute les informations du livre à la liste
                print(book_info)  # Affiche les informations du livre
        category_name = category_url.rsplit('/', 2)[-2]  # Extrait le nom de la catégorie à partir de l'URL
        write_to_csv(category_name, books)  # Écrit les informations des livres dans un fichier CSV
