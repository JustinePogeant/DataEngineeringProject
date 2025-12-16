import pymongo
import redis
import psycopg2
from psycopg2.extras import Json
import json
import os
from datetime import datetime


class MongoDBPipeline:
    """Pipeline pour sauvegarder les données dans MongoDB"""
    
    def __init__(self):
        self.mongo_uri = os.getenv('MONGODB_URI', 'mongodb://admin:routard123@localhost:27017/')
        self.mongo_db = os.getenv('MONGODB_DATABASE', 'routard_db')
        self.client = None
        self.db = None

    def open_spider(self, spider):
        """Connexion à MongoDB au démarrage du spider"""
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        spider.logger.info(f"Connected to MongoDB: {self.mongo_db}")

    def close_spider(self, spider):
        """Fermeture de la connexion à la fin"""
        if self.client:
            self.client.close()
            spider.logger.info("MongoDB connection closed")

    def process_item(self, item, spider):
        """Traite et sauvegarde chaque item"""
        # Déterminer la collection selon le type de spider
        if spider.name in ['european_capitals', 'european_capitals_alt']:
            collection_name = 'capitales'
            key_field = 'capitale'
        else:
            collection_name = 'destinations'
            key_field = 'nom'
        
        # Convertir l'item en dictionnaire
        item_dict = dict(item)
        
        # Vérifier si l'item existe déjà
        existing = self.db[collection_name].find_one({key_field: item_dict.get(key_field)})
        
        if existing:
            # Mise à jour
            self.db[collection_name].update_one(
                {'_id': existing['_id']},
                {'$set': item_dict}
            )
            spider.logger.info(f"Updated {key_field}: {item_dict.get(key_field)}")
        else:
            # Insertion
            self.db[collection_name].insert_one(item_dict)
            spider.logger.info(f"Inserted {key_field}: {item_dict.get(key_field)}")
        
        return item


class RedisCachePipeline:
    """Pipeline pour mettre en cache les données dans Redis"""
    
    def __init__(self):
        self.redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.redis_port = int(os.getenv('REDIS_PORT', 6379))
        self.redis_client = None
        self.ttl = 3600  # 1 heure

    def open_spider(self, spider):
        """Connexion à Redis"""
        self.redis_client = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            decode_responses=True
        )
        spider.logger.info(f"Connected to Redis: {self.redis_host}:{self.redis_port}")

    def close_spider(self, spider):
        """Fermeture de la connexion Redis"""
        if self.redis_client:
            self.redis_client.close()
            spider.logger.info("Redis connection closed")

    def process_item(self, item, spider):
        """Cache l'item dans Redis"""
        item_dict = dict(item)
        key = f"destination:{item_dict.get('nom')}"
        
        # Sérialiser en JSON
        value = json.dumps(item_dict, default=str)
        
        # Stocker avec TTL
        self.redis_client.setex(key, self.ttl, value)
        spider.logger.debug(f"Cached in Redis: {key}")
        
        return item


class PostgreSQLPipeline:
    """Pipeline pour stocker les statistiques dans PostgreSQL"""
    
    def __init__(self):
        self.host = os.getenv('POSTGRES_HOST', 'localhost')
        self.port = int(os.getenv('POSTGRES_PORT', 5432))
        self.user = os.getenv('POSTGRES_USER', 'routard_user')
        self.password = os.getenv('POSTGRES_PASSWORD', 'routard123')
        self.database = os.getenv('POSTGRES_DB', 'routard_stats')
        self.connection = None
        self.cursor = None

    def open_spider(self, spider):
        """Connexion à PostgreSQL"""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.connection.cursor()
            
            # Créer la table si elle n'existe pas
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS destinations_stats (
                    id SERIAL PRIMARY KEY,
                    nom VARCHAR(255) UNIQUE,
                    continent VARCHAR(100),
                    budget VARCHAR(50),
                    nb_attractions INTEGER,
                    nb_conseils INTEGER,
                    date_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.connection.commit()
            spider.logger.info("Connected to PostgreSQL")
        except Exception as e:
            spider.logger.error(f"Error connecting to PostgreSQL: {e}")

    def close_spider(self, spider):
        """Fermeture des connexions"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            spider.logger.info("PostgreSQL connection closed")

    def process_item(self, item, spider):
        """Enregistre les statistiques"""
        item_dict = dict(item)
        
        try:
            # Insérer ou mettre à jour les statistiques
            self.cursor.execute("""
                INSERT INTO destinations_stats 
                (nom, continent, budget, nb_attractions, nb_conseils, date_update)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (nom) 
                DO UPDATE SET 
                    continent = EXCLUDED.continent,
                    budget = EXCLUDED.budget,
                    nb_attractions = EXCLUDED.nb_attractions,
                    nb_conseils = EXCLUDED.nb_conseils,
                    date_update = EXCLUDED.date_update
            """, (
                item_dict.get('nom'),
                item_dict.get('continent'),
                item_dict.get('budget_moyen'),
                len(item_dict.get('attractions', [])),
                len(item_dict.get('conseils_pratiques', [])),
                datetime.now()
            ))
            self.connection.commit()
            spider.logger.debug(f"Stats saved for: {item_dict.get('nom')}")
        except Exception as e:
            spider.logger.error(f"Error saving stats: {e}")
            self.connection.rollback()
        
        return item


class DataCleaningPipeline:
    """Pipeline pour nettoyer et valider les données"""
    
    def process_item(self, item, spider):
        """Nettoie les données de l'item"""
        item_dict = dict(item)
        
        # Validation du nom
        if not item_dict.get('nom') or item_dict['nom'].strip() == '':
            spider.logger.warning("Item dropped: nom manquant")
            raise DropItem("Nom de destination manquant")
        
        # Normalisation du budget
        if not item_dict.get('budget_moyen'):
            item['budget_moyen'] = "Non spécifié"
        
        # S'assurer que les listes sont bien des listes
        for field in ['conseils_pratiques', 'attractions', 'langues', 'meilleure_periode']:
            if field not in item_dict or not isinstance(item_dict[field], list):
                item[field] = []
        
        # Validation de l'URL
        url = item_dict.get('url', '')
        if not url.startswith('http'):
            spider.logger.warning(f"URL invalide: {url}")
        
        return item


from scrapy.exceptions import DropItem