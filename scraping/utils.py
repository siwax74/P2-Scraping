#########################################################################################
#                                                                                       #
#                            Utils.py                                                   #
#                                                                                       #
# Auteur: Damien Gey                                                                    #
# Date de Création: 17/07/24                                                            #
# Description: Ce fichier Utils.py contient les fonctions réutilisable                   #
#                                                                                       #
# Modules Importés:                                                                     #
# - os: opérations sur le système de fichiers                                           #
# - re: expressions régulières                                                          #
# - typing: annotations de type                                                         #
# - bs4 (BeautifulSoup): parsing HTML                                                   #
# - requests: requêtes HTTP                                                             #
#########################################################################################
import os
import re
from typing import Optional
from bs4 import BeautifulSoup
import requests


def sanitize_filename(filename: str) -> str:
    """
    Nettoie un nom de fichier en retirant les caractères non valides.
    
    Args:
        filename (str): Le nom de fichier à nettoyer.
    
    Returns:
        str: Le nom de fichier nettoyé.
    """
    return re.sub(r'[<>:"/\\|?*]', '', filename)  
def download_image(image_url: str, category_name: str, image_name: str) -> None:
    """
    Télécharge une image à partir d'une URL et la sauve dans un dossier spécifié.
    
    Args:
        image_url (str): L'URL de l'image à télécharger.
        category_name (str): Nom de la catégorie à laquelle appartient l'image.
        image_name (str): Nom de l'image à sauvegarder.
    """
    try:
        response = requests.get(image_url) 
        response.raise_for_status()
        if response.status_code == 200: 
            category_folder = os.path.join("images", sanitize_filename(category_name))
            os.makedirs(category_folder, exist_ok=True)
            image_name = sanitize_filename(image_name)
            image_path = os.path.join(category_folder, image_name)
            with open(image_path, 'wb') as file:
                file.write(response.content)
        else:
            print(f"Échec du téléchargement de l'image depuis {image_url}")
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du téléchargement de l'image depuis {image_url}: {e}")

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
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération de {url}: {e}")
        return None
    
