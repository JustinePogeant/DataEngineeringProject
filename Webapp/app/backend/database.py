from pymongo import MongoClient
import os

# On remplace 'db' par 'mongodb_guide' qui est le vrai nom de ton service Docker
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongodb_guide:27017/')

class DatabaseManager:
    def __init__(self):
        # On ajoute un petit timeout pour éviter que le site mouline dans le vide
        self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        self.db = self.client['guide_voyage']
        self.capitales = self.db['capitales']
        self.restaurants = self.db['restaurants']

    def get_all_capitals(self):
        return list(self.capitales.find({}, {'_id': 0}))

    def get_restaurants_by_city(self, city_name):
        # On utilise une recherche insensible à la casse pour être sûr de trouver les restos
        return list(self.restaurants.find(
            {'capitale': {'$regex': f"^{city_name}$", '$options': 'i'}}, 
            {'_id': 0}
        ))

db_manager = DatabaseManager()
