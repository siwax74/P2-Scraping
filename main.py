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
#   - get_categories(): Récupère les URLs des catégories à partir de la page d'accueil. #
#   - extract_book_info(): Extrait les informations détaillées d'un livre.              #
#   - get_books_in_category(): Récupère les URLs des livres dans une catégorie.         #
#                                                                                       #
#   - write_to_csv(): Écrit les informations des livres dans un fichier CSV.            #
#                                                                                       #
#########################################################################################

import pprint
from scraping.get_books_data import extract_book_info, get_books_in_category, get_categories, write_to_csv

def etl(url: str) -> None:                     
    """
    Fonction principale qui effectue l'ETL (Extraction, Transformation, Load) pour le site de livres.
    
    Args:
        url (str): L'URL de la page d'accueil du site de livres.
    """
    categories = get_categories(url)           
    if not categories:                         
        pprint.pprint("Aucune catégorie trouvée.")  
        return                                  
    
    for category_url in categories:    
        category_title = category_url.rsplit('/', 2)[-2].replace('-', ' ').title()   
        pprint.pprint(f"Extraction de la catégorie: {category_title}")  
        books = []                              
        book_urls = get_books_in_category(category_url)  
        if not book_urls:                       
            pprint.pprint(f"Aucun livre trouvé dans la catégorie {category_url}.")  
            continue                            
        
        for book_url in book_urls:              
            book_title = book_url.rsplit('/', 2)[-2].replace('-', ' ').title()
            pprint.pprint(f"  Extraction du livre: {book_title} de cette catégories")  
            book_info = extract_book_info(book_url)  
            if book_info:                      
                books.append(book_info)         
        
        category_name = category_url.rsplit('/', 2)[-2] 
        write_to_csv(category_name, books)

if __name__ == "__main__":
    url = "https://books.toscrape.com/"
    etl(url)
