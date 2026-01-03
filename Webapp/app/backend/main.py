from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from elasticsearch import Elasticsearch
import os
from utils import get_city_coordinates

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION DES URIS DOCKER ---
# On utilise les noms des services définis dans ton docker-compose.yml
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb_guide:27017/")
ES_URL = os.getenv("ES_HOST", "http://elasticsearch_guide:9200")

# Connexions
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['guide_voyage']
# Configuration robuste pour Elasticsearch
es = Elasticsearch([ES_URL], retry_on_timeout=True, max_retries=3)

def clean_city_name(name):
    """Nettoie le nom pour correspondre au dictionnaire de coordonnées"""
    if not name: return ""
    clean = name
    # 1. Retrait des préfixes de guide
    prefixes = ["Guide de voyage et vacances à ", "Guide de voyage ", "Visiter ", "Vacances à "]
    for prefix in prefixes:
        clean = clean.replace(prefix, "")
    
    # 2. TRÈS IMPORTANT : On coupe à la virgule pour éviter "Nicosie, Chypre"
    # Cela permet de trouver "Nicosie" dans ton dictionnaire utils.py
    clean = clean.split(',')[0].strip()
    return clean

@app.route('/api/capitals', methods=['GET'])
def get_capitals():
    try:
        # On récupère tout de MongoDB sans filtre pour garder photos et liens
        capitales = list(db['capitales'].find({}, {'_id': 0}))
        for cap in capitales:
            nom_propre = clean_city_name(cap.get('capitale', ''))
            cap['capitale_display'] = nom_propre
            
            # Récupération des coordonnées (utils.py)
            coords = get_city_coordinates(nom_propre)
            cap['lat'] = coords[0]
            cap['lon'] = coords[1]
        return jsonify(capitales)
    except Exception as e:
        print(f"Erreur Mongo: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip()
    if not query: return jsonify([])

    # Requête Elasticsearch compatible avec ta version
    body = {
        "query": {
            "bool": {
                "should": [
                    { "match_phrase_prefix": { "capitale": { "query": query, "boost": 10 } } },
                    { "match": { "capitale": { "query": query, "fuzziness": "AUTO" } } }
                ]
            }
        }
    }
    
    try:
        # Utilisation de 'body' pour la recherche Elastic
        res = es.search(index="capitales", body=body)
        results = [hit["_source"] for hit in res["hits"]["hits"]]
        for r in results:
            nom_propre = clean_city_name(r.get('capitale', ''))
            r['capitale_display'] = nom_propre
            coords = get_city_coordinates(nom_propre)
            r['lat'] = coords[0]
            r['lon'] = coords[1]
        return jsonify(results)
    except Exception as e:
        print(f"Erreur Elastic Search: {e}")
        return jsonify([])

@app.route('/api/restaurants/<city_name>', methods=['GET'])
def get_restaurants(city_name):
    try:
        # On nettoie le nom reçu pour la requête Mongo
        clean = clean_city_name(city_name)
        query = {"$or": [
            {"capitale": {"$regex": f"^{clean}$", "$options": "i"}},
            {"ville": {"$regex": f"^{clean}$", "$options": "i"}}
        ]}
        restos = list(db['restaurants'].find(query, {'_id': 0}))
        return jsonify(restos)
    except Exception as e:
        print(f"Erreur Restaurants: {e}")
        return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)