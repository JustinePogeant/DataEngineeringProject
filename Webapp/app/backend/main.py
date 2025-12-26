from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os
import re

app = Flask(__name__)
CORS(app)

# Connexion à MongoDB
try:
    client = MongoClient("mongodb://mongodb_guide:27017/", serverSelectionTimeoutMS=5000)
    db = client['guide_voyage']
    capitales_col = db['capitales']
    restaurants_col = db['restaurants']
except Exception as e:
    print(f"Erreur de connexion MongoDB: {e}")

def deep_clean(text):
    if not text: return ""
    clean = re.sub(r'<.*?>', '', str(text))
    clean = " ".join(clean.split())
    return clean.strip()

@app.route('/api/capitals', methods=['GET'])
def get_capitals():
    try:
        cities = list(capitales_col.find({}, {'_id': 0}))
        for city in cities:
            if 'description' in city:
                city['description'] = deep_clean(city.get('description', ''))
        return jsonify(cities)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/restaurants/<capitale>', methods=['GET'])
def get_restaurants_by_city(capitale):
    try:
        # Recherche insensible à la casse
        restos = list(restaurants_col.find(
            {"capitale": {"$regex": f"^{capitale}$", "$options": "i"}}, 
            {'_id': 0}
        ))
        # Transformation du prix 999
        for r in restos:
            if str(r.get('prix_niveau')) == "999":
                r['prix_niveau'] = "Prix non spécifié"
        return jsonify(restos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)