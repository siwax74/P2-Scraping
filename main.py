#########################################################################################
#                                                                                       #
#                             SCRIPT DE SCRAPING                                        #
#                                                                                       #
# Auteur: Damien Gey                                                                    #
# Date de Création: 17/07/24                                                            #
# Description: Ce script permet de scraper les informations des livres à partir         #
#              d'un site web, incluant les catégories, les livres, les images           #
#              et les détails des livres, puis de sauvegarder ces informations          #
#              dans des fichiers CSV.                                                   #
#                                                                                       #
# Modules Importés:                                                                     #
# - pprint: Pour afficher les informations de manière structurée.                       #
# - scraping.get_books_data.py: Contient les fonctions pour extraire les données.       #
#   - extract_book_info(): Extrait les informations détaillées d'un livre.              #
#   - get_books_in_category(): Récupère les URLs des livres dans une catégorie.         #
#   - get_categories(): Récupère les URLs des catégories à partir de la page d'accueil. #
#   - write_to_csv(): Écrit les informations des livres dans un fichier CSV.            #
#                                                                                       #
#########################################################################################

import pprint
from scraping.get_books_data import extract_book_info, get_books_in_category, get_categories, write_to_csv

def etl(url: str) -> None:                      # Définition de la fonction principale ETL
    """
    Fonction principale qui effectue l'ETL (Extraction, Transformation, Load) pour le site de livres.
    
    Args:
        url (str): L'URL de la page d'accueil du site de livres.
    """
    categories = get_categories(url)            # Récupère les URLs des catégories
    if not categories:                          # Vérifie si aucune catégorie n'a été trouvée
        pprint.pprint("Aucune catégorie trouvée.")  # Affiche un message si aucune catégorie n'a été trouvée
        return                                  # Sort de la fonction si aucune catégorie
    
    for category_url in categories:    
        category_title = category_url.rsplit('/', 2)[-2].replace('-', ' ').title()   # Boucle sur chaque URL de catégorie
        pprint.pprint(f"Extraction de la catégorie: {category_title}")  # Affiche l'URL de la catégorie en cours d'extraction
        books = []                              # Initialise une liste pour les livres
        book_urls = get_books_in_category(category_url)  # Récupère les URLs des livres dans la catégorie
        if not book_urls:                       # Vérifie si aucune URL de livre n'a été trouvée
            pprint.pprint(f"Aucun livre trouvé dans la catégorie {category_url}.")  # Affiche un message si aucun livre n'a été trouvé
            continue                            # Passe à la catégorie suivante
        
        for book_url in book_urls:              # Boucle sur chaque URL de livre
            book_title = book_url.rsplit('/', 2)[-2].replace('-', ' ').title()
            pprint.pprint(f"  Extraction du livre: {book_title} de cette catégories")  # Affiche le titre du livre en cours d'extractio
            book_info = extract_book_info(book_url)  # Extrait les informations du livre
            if book_info:                       # Vérifie si les informations du livre ont été extraites avec succès
                books.append(book_info)         # Ajoute les informations du livre à la liste
        
        category_name = category_url.rsplit('/', 2)[-2]  # Extrait le nom de la catégorie à partir de l'URL
        write_to_csv(category_name, books)      # Écrit les informations des livres dans un fichier CSV

if __name__ == "__main__":
    url = "https://books.toscrape.com/"
    etl(url)
