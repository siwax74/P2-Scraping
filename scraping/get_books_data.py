import re  # Importation du module re pour les expressions régulières
import os  # Importation du module os pour les opérations sur le système de fichiers
import csv  # Importation du module csv pour écrire des fichiers CSV
from urllib.parse import urljoin, urlparse  # Importation de fonctions pour manipuler les URLs
import requests  # Importation du module requests pour effectuer des requêtes HTTP
from bs4 import BeautifulSoup  # Importation de BeautifulSoup pour parser le HTML

def extract_soup(url):
    """
    Extrait et retourne un objet BeautifulSoup à partir de l'URL donnée.
    
    Args:
        url (str): L'URL à partir de laquelle extraire le BeautifulSoup.
    
    Returns:
        BeautifulSoup: Objet BeautifulSoup parsé à partir du contenu HTML de l'URL.
        None: Retourne None si une exception est levée lors de la requête.
    """
    try:
        response = requests.get(url)  # Effectue une requête GET à l'URL
        response.raise_for_status()  # Lève une exception si la requête échoue
        return BeautifulSoup(response.content, "html.parser")  # Parse le contenu HTML avec BeautifulSoup
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération de {url}: {e}")  # Affiche une erreur si la requête échoue
        return None  # Retourne None en cas d'exception

def get_categories(url):
    """
    Récupère les URLs des catégories à partir de la page d'accueil du site.
    
    Args:
        url (str): L'URL de la page d'accueil du site.
    
    Returns:
        list: Liste des URLs des catégories trouvées sur la page.
    """
    soup = extract_soup(url)  # Extrait et parse le contenu HTML de l'URL
    if not soup:
        return []  # Retourne une liste vide si l'extraction échoue
    
    categories = soup.find('ul', class_='nav nav-list').find_all('li')[1:]  # Trouve les catégories de livres
    category_urls = [urljoin(url, category.find('a')['href']) for category in categories]  # Génère les URLs des catégories
    return category_urls  # Retourne la liste des URLs des catégories

def get_books_in_category(category_url):
    """
    Récupère les URLs des livres dans une catégorie donnée.
    
    Args:
        category_url (str): L'URL de la catégorie à scraper.
    
    Returns:
        list: Liste des URLs des livres trouvés dans la catégorie.
    """
    book_urls = []  # Initialise une liste pour les URLs des livres
    while category_url:
        soup = extract_soup(category_url)  # Extrait et parse le contenu HTML de l'URL de la catégorie
        if not soup:
            break  # Sort de la boucle si l'extraction échoue
        
        for article in soup.find_all('article', class_='product_pod'):
            book_url = urljoin(category_url, article.find('h3').find('a')['href'])  # Génère l'URL du livre
            book_urls.append(book_url)  # Ajoute l'URL du livre à la liste
        
        next_button = soup.find('li', class_='next')  # Trouve le bouton "Next" pour la pagination
        category_url = urljoin(category_url, next_button.find('a')['href']) if next_button else None  # Met à jour l'URL pour la page suivante
    
    return book_urls  # Retourne la liste des URLs des livres

def sanitize_filename(filename):
    """
    Nettoie un nom de fichier en retirant les caractères non valides.
    
    Args:
        filename (str): Le nom de fichier à nettoyer.
    
    Returns:
        str: Le nom de fichier nettoyé.
    """
    return re.sub(r'[<>:"/\\|?*]', '', filename)  # Nettoie le nom de fichier en retirant les caractères non valides

def download_image(image_url, category_name, image_name):
    """
    Télécharge une image à partir d'une URL et la sauve dans un dossier spécifié.
    
    Args:
        image_url (str): L'URL de l'image à télécharger.
        category_name (str): Nom de la catégorie à laquelle appartient l'image.
        image_name (str): Nom de l'image à sauvegarder.
    """
    try:
        response = requests.get(image_url)  # Effectue une requête GET à l'URL de l'image
        response.raise_for_status()  # Lève une exception si la requête échoue
        if response.status_code == 200:
            category_folder = os.path.join("images", category_name)  # Crée le chemin du dossier de la catégorie
            os.makedirs(category_folder, exist_ok=True)  # Crée le dossier si il n'existe pas déjà
            image_name = sanitize_filename(image_name)  # Nettoie le nom de l'image
            image_path = os.path.join(category_folder, image_name)  # Génère le chemin complet de l'image
            with open(image_path, 'wb') as file:  # Ouvre le fichier en mode écriture binaire
                file.write(response.content)  # Écrit le contenu de l'image dans le fichier
        else:
            print(f"Échec du téléchargement de l'image depuis {image_url}")  # Affiche une erreur si le téléchargement échoue
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du téléchargement de l'image depuis {image_url}: {e}")  # Affiche une erreur en cas d'exception

def extract_book_info(book_url):
    """
    Extrait les informations d'un livre à partir de son URL.
    
    Args:
        book_url (str): L'URL du livre à scraper.
    
    Returns:
        dict: Dictionnaire contenant les informations extraites du livre.
    """
    soup = extract_soup(book_url)  # Extrait et parse le contenu HTML de l'URL du livre
    if not soup:
        return {}  # Retourne un dictionnaire vide si l'extraction échoue
    
    book_info = {}
    book_info['product_page_url'] = book_url
    book_info['upc'] = soup.find('th', string='UPC').find_next('td').text.strip()  # Extrait l'UPC du livre
    book_info['title'] = soup.find('h1').text.strip()  # Extrait le titre du livre
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
    
    return book_info  # Retourne les informations du livre

def write_to_csv(category_name, books):
    """
    Écrit les informations des livres dans un fichier CSV pour une catégorie donnée.
    
    Args:
        category_name (str): Nom de la catégorie pour laquelle écrire le fichier CSV.
        books (list): Liste des livres à écrire dans le fichier CSV.
    """
    filename = f"{category_name}.csv"  # Génère le nom du fichier CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:  # Ouvre le fichier CSV en mode écriture
        fieldnames = ['product_page_url', 'upc', 'title', 'price_incl_tax', 'price_excl_tax', 'availability', 'description', 'category', 'rating', 'image_url', 'image_path']  # Définit les en-têtes de colonnes
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
