# -*- coding: utf-8 -*-
"""
MongoDB Pipeline for Travel & Restaurant Scraper
Handles data validation, cleaning, and storage in MongoDB
"""

import pymongo
from datetime import datetime
from scrapy.exceptions import DropItem
import logging


class MongoDBPipeline:
    """
    Pipeline principal pour stocker les données dans MongoDB
    Gère les capitales et les restaurants dans des collections séparées
    """
    
    # Configuration MongoDB
    MONGO_URI = 'mongodb://localhost:27017/'
    MONGO_DATABASE = 'guide_voyage'
    
    def __init__(self):
        self.client = None
        self.db = None
        self.capitale_collection = None
        self.restaurant_collection = None
        self.stats = {
            'capitales_inserted': 0,
            'capitales_updated': 0,
            'capitales_dropped': 0,
            'restaurants_inserted': 0,
            'restaurants_updated': 0,
            'restaurants_dropped': 0
        }
    
    @classmethod
    def from_crawler(cls, crawler):
        """
        Méthode appelée par Scrapy pour créer le pipeline
        Permet de récupérer les settings du projet
        """
        pipeline = cls()
        
        # Override avec les settings du projet si disponibles
        pipeline.MONGO_URI = crawler.settings.get('MONGO_URI', cls.MONGO_URI)
        pipeline.MONGO_DATABASE = crawler.settings.get('MONGO_DATABASE', cls.MONGO_DATABASE)
        
        return pipeline
    
    def open_spider(self, spider):
        """
        Appelé à l'ouverture du spider
        Initialise la connexion MongoDB
        """
        try:
            self.client = pymongo.MongoClient(self.MONGO_URI)
            self.db = self.client[self.MONGO_DATABASE]
            
            # Création des collections
            self.capitale_collection = self.db['capitales']
            self.restaurant_collection = self.db['restaurants']
            
            # Création des index pour optimiser les requêtes
            self._create_indexes()
            
            spider.logger.info(f'🔗 Connexion MongoDB établie: {self.MONGO_DATABASE}')
            
        except Exception as e:
            spider.logger.error(f'Erreur connexion MongoDB: {str(e)}')
            raise
    
    def close_spider(self, spider):
        """
        Appelé à la fermeture du spider
        Ferme la connexion et affiche les statistiques
        """
        if self.client:
            self.client.close()
            spider.logger.info('🔌 Connexion MongoDB fermée')
        
        # Affichage des statistiques
        spider.logger.info('Statistiques de scraping:')
        spider.logger.info(f'   Capitales - Insérées: {self.stats["capitales_inserted"]}, '
                          f'Mises à jour: {self.stats["capitales_updated"]}, '
                          f'Rejetées: {self.stats["capitales_dropped"]}')
        spider.logger.info(f'   Restaurants - Insérés: {self.stats["restaurants_inserted"]}, '
                          f'Mis à jour: {self.stats["restaurants_updated"]}, '
                          f'Rejetés: {self.stats["restaurants_dropped"]}')
    
    def _create_indexes(self):
        """
        Crée les index MongoDB pour optimiser les performances
        """
        # Index pour les capitales
        self.capitale_collection.create_index('capitale', unique=True)
        self.capitale_collection.create_index('date_scraping')
        
        # Index composé pour les restaurants (unicité sur nom + capitale)
        self.restaurant_collection.create_index(
            [('nom', pymongo.ASCENDING), ('capitale', pymongo.ASCENDING)],
            unique=True
        )
        self.restaurant_collection.create_index('capitale')
        self.restaurant_collection.create_index('type_cuisine')
        self.restaurant_collection.create_index('prix_niveau')
        self.restaurant_collection.create_index('date_scraping')
    
    def process_item(self, item, spider):
        """
        Traite chaque item scrappé
        Route vers la méthode appropriée selon le type d'item
        """
        # Détermine le type d'item en fonction des champs présents
        if 'quand_partir' in item or 'decalage' in item:
            return self._process_capitale(item, spider)
        elif 'nom' in item and 'adresse' in item:
            return self._process_restaurant(item, spider)
        else:
            spider.logger.warning(f'⚠️  Type d\'item inconnu: {item}')
            raise DropItem('Type d\'item non reconnu')
    
    def _process_capitale(self, item, spider):
        """
        Traite et stocke un item de type Capitale
        """
        try:
            # Validation
            if not item.get('capitale'):
                spider.logger.warning('⚠️  Item capitale sans nom de capitale')
                self.stats['capitales_dropped'] += 1
                raise DropItem('Capitale manquante')
            
            # Nettoyage des données
            clean_item = self._clean_capitale_data(item)
            
            # Insertion ou mise à jour (upsert)
            result = self.capitale_collection.update_one(
                {'capitale': clean_item['capitale']},
                {'$set': clean_item},
                upsert=True
            )
            
            if result.upserted_id:
                self.stats['capitales_inserted'] += 1
                spider.logger.debug(f'✅ Capitale insérée: {clean_item["capitale"]}')
            elif result.modified_count > 0:
                self.stats['capitales_updated'] += 1
                spider.logger.debug(f'🔄 Capitale mise à jour: {clean_item["capitale"]}')
            
            return item
            
        except Exception as e:
            spider.logger.error(f'❌ Erreur traitement capitale: {str(e)}')
            self.stats['capitales_dropped'] += 1
            raise DropItem(f'Erreur: {str(e)}')
    
    def _process_restaurant(self, item, spider):
        """
        Traite et stocke un item de type Restaurant
        """
        try:
            # Validation
            if not item.get('nom') or not item.get('capitale'):
                spider.logger.warning(f'⚠️  Item restaurant incomplet: {item.get("nom", "?")}')
                self.stats['restaurants_dropped'] += 1
                raise DropItem('Nom ou capitale manquant')
            
            # Nettoyage des données
            clean_item = self._clean_restaurant_data(item)
            
            # Insertion ou mise à jour (upsert)
            result = self.restaurant_collection.update_one(
                {'nom': clean_item['nom'], 'capitale': clean_item['capitale']},
                {'$set': clean_item},
                upsert=True
            )
            
            if result.upserted_id:
                self.stats['restaurants_inserted'] += 1
                spider.logger.debug(f'✅ Restaurant inséré: {clean_item["nom"]} ({clean_item["capitale"]})')
            elif result.modified_count > 0:
                self.stats['restaurants_updated'] += 1
                spider.logger.debug(f'🔄 Restaurant mis à jour: {clean_item["nom"]} ({clean_item["capitale"]})')
            
            return item
            
        except Exception as e:
            spider.logger.error(f'❌ Erreur traitement restaurant: {str(e)}')
            self.stats['restaurants_dropped'] += 1
            raise DropItem(f'Erreur: {str(e)}')
    
    def _clean_capitale_data(self, item):
        """
        Nettoie et normalise les données d'une capitale
        """
        clean = {}
        
        # Champs obligatoires
        clean['capitale'] = str(item['capitale']).strip()
        
        # Champs optionnels
        if item.get('description'):
            clean['description'] = str(item['description']).strip()
        
        if item.get('quand_partir'):
            clean['quand_partir'] = str(item['quand_partir']).strip()
        
        if item.get('decalage'):
            clean['decalage'] = str(item['decalage']).strip()
        
        if item.get('url'):
            clean['url'] = str(item['url']).strip()
        
        # Date de scraping
        clean['date_scraping'] = item.get('date_scraping', datetime.now().strftime("%d/%m/%Y"))
        
        # Métadonnées
        clean['last_updated'] = datetime.now()
        
        # Supprime les champs None ou vides
        clean = {k: v for k, v in clean.items() if v not in [None, '', 'null']}
        
        return clean
    
    def _clean_restaurant_data(self, item):
        """
        Nettoie et normalise les données d'un restaurant
        """
        clean = {}
        
        # Champs obligatoires
        clean['nom'] = str(item['nom']).strip()
        clean['capitale'] = str(item['capitale']).strip()
        
        # Champs optionnels
        if item.get('adresse'):
            clean['adresse'] = str(item['adresse']).strip()
        
        if item.get('type_cuisine') and item['type_cuisine'] not in ['null', None]:
            clean['type_cuisine'] = str(item['type_cuisine']).strip()
        
        if item.get('description'):
            clean['description'] = str(item['description']).strip()
        
        # Prix - normalisation
        if item.get('prix_niveau'):
            prix = item['prix_niveau']
            if isinstance(prix, str) and prix != 'null':
                # Compte les symboles €
                clean['prix_niveau'] = prix.count('€')
            elif isinstance(prix, int):
                clean['prix_niveau'] = prix
        
        if item.get('telephone'):
            clean['telephone'] = str(item['telephone']).strip()
        
        if item.get('site_web'):
            clean['site_web'] = str(item['site_web']).strip()
        
        # Images - s'assure que c'est une liste
        if item.get('images'):
            if isinstance(item['images'], list):
                clean['images'] = [img.strip() for img in item['images'] if img]
            else:
                clean['images'] = [str(item['images']).strip()]
        
        if item.get('url'):
            clean['url'] = str(item['url']).strip()
        
        # Date de scraping - format ISO
        if item.get('date_scraping'):
            clean['date_scraping'] = item['date_scraping']
        else:
            clean['date_scraping'] = datetime.now().isoformat()
        
        # Métadonnées
        clean['last_updated'] = datetime.now()
        
        # Supprime les champs None ou vides
        clean = {k: v for k, v in clean.items() if v not in [None, '', 'null', []]}
        
        return clean


class DataValidationPipeline:
    """
    Pipeline de validation des données avant insertion
    S'exécute AVANT le MongoDBPipeline
    """
    
    def process_item(self, item, spider):
        """
        Valide les données de l'item
        """
        # Validation des URLs
        if item.get('url') and not self._is_valid_url(item['url']):
            spider.logger.warning(f'⚠️  URL invalide: {item.get("url")}')
            raise DropItem('URL invalide')
        
        # Validation des images
        if item.get('images'):
            if isinstance(item['images'], list):
                valid_images = [img for img in item['images'] if self._is_valid_url(img)]
                item['images'] = valid_images
            elif not self._is_valid_url(item['images']):
                del item['images']
        
        return item
    
    @staticmethod
    def _is_valid_url(url):
        """
        Vérifie si une URL est valide
        """
        if not url or url == 'null':
            return False
        return url.startswith(('http://', 'https://'))


class DuplicateFilterPipeline:
    """
    Pipeline pour détecter et logger les doublons
    Garde une trace des items déjà vus dans cette session
    """
    
    def __init__(self):
        self.seen_capitales = set()
        self.seen_restaurants = set()
    
    def process_item(self, item, spider):
        """
        Vérifie si l'item a déjà été vu
        """
        # Pour les capitales
        if 'quand_partir' in item or 'decalage' in item:
            capitale = item.get('capitale')
            if capitale in self.seen_capitales:
                spider.logger.debug(f'🔄 Doublon capitale détecté: {capitale}')
            else:
                self.seen_capitales.add(capitale)
        
        # Pour les restaurants
        elif 'nom' in item and 'adresse' in item:
            resto_id = f"{item.get('nom')}_{item.get('capitale')}"
            if resto_id in self.seen_restaurants:
                spider.logger.debug(f'🔄 Doublon restaurant détecté: {resto_id}')
            else:
                self.seen_restaurants.add(resto_id)
        
        return item


# Configuration des pipelines dans settings.py:
"""
ITEM_PIPELINES = {
    'your_project.pipelines.DataValidationPipeline': 100,
    'your_project.pipelines.DuplicateFilterPipeline': 200,
    'your_project.pipelines.MongoDBPipeline': 300,
}

# Configuration MongoDB
MONGO_URI = 'mongodb://localhost:27017/'
MONGO_DATABASE = 'travel_guide'
"""