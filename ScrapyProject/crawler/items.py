# -*- coding: utf-8 -*-
"""
Items definition for Travel & Restaurant Scraper
Defines the data structures for capitals and restaurants
"""

import scrapy
from datetime import datetime
from scrapy.item import Item, Field


class CapitaleItem(scrapy.Item):
    """
    Item pour les données de capitales scrappées depuis le guide du routard
    """
    # Identifiant unique, on utilise la capitale comme clé
    capitale = Field()
    
    # Informations descriptives
    description = Field()
    quand_partir = Field()
    decalage = Field()
    
    # Métadonnées
    url = Field()
    date_scraping = Field()
    
    # Champs optionnels pour enrichissement futur
    pays = Field()
    continent = Field()
    population = Field()
    langue = Field()
    monnaie = Field()


class RestaurantItem(scrapy.Item):
    """
    Item pour les données de restaurants scrappées depuis le guide Michelin
    """
    # Identifiant - combinaison nom + capitale pour unicité
    nom = Field()
    capitale = Field()
    
    # Informations de base
    adresse = Field()
    type_cuisine = Field()
    description = Field()
    
    # Informations pratiques
    prix_niveau = Field()  # Nombre de symboles € (ou 999 pour non spécifié)
    telephone = Field()
    site_web = Field()
    
    # Médias
    images = Field()  # Liste d'URLs
    
    # Métadonnées
    url = Field()
    date_scraping = Field()
    
    # Champs optionnels pour enrichissement futur
    horaires = Field()
    services = Field()  # Liste: terrasse, parking, wifi, etc.
    note_michelin = Field()  # étoiles, bib gourmand, etc.
    specialites = Field()  # Liste de plats signature


# Classes d'aide pour la validation et la normalisation
class ItemValidator:
    """
    Classe utilitaire pour valider et nettoyer les items avant insertion
    """
    
    @staticmethod
    def validate_capitale(item):
        """
        Valide un CapitaleItem
        """
        if not item.get('capitale'):
            raise ValueError("Le champ 'capitale' est obligatoire")
        
        # Ajoute la date de scraping si absente
        if not item.get('date_scraping'):
            item['date_scraping'] = datetime.now().strftime("%d/%m/%Y")
        
        return item
    
    @staticmethod
    def validate_restaurant(item):
        """
        Valide un RestaurantItem
        """
        if not item.get('nom'):
            raise ValueError("Le champ 'nom' est obligatoire")
        
        if not item.get('capitale'):
            raise ValueError("Le champ 'capitale' est obligatoire")
        
        # Convertit la date en ISO format pour MongoDB
        if item.get('date_scraping'):
            try:
                # Si c'est déjà une string ISO, on la garde
                if isinstance(item['date_scraping'], str) and 'T' in item['date_scraping']:
                    pass
                else:
                    # Sinon on convertit
                    item['date_scraping'] = datetime.now().isoformat()
            except:
                item['date_scraping'] = datetime.now().isoformat()
        else:
            item['date_scraping'] = datetime.now().isoformat()
        
        # Normalise les images en liste
        if item.get('images') and not isinstance(item['images'], list):
            item['images'] = [item['images']]
        
        return item
    
    @staticmethod
    def normalize_price_level(price_str):
        """
        Normalise le niveau de prix (€, €€, €€€, etc.)
        Retourne un entier: 1, 2, 3, ou 999 si non spécifié
        """
        if not price_str or price_str == 'null':
            return 999
        
        if isinstance(price_str, int):
            return price_str
        
        # Compte le nombre de symboles €
        count = price_str.count('€')
        return count if count > 0 else 999