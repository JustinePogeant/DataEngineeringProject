import os
from pymongo import MongoClient
from elasticsearch import Elasticsearch, helpers
import time



# On essaie de lire les variables d'environnement, sinon on met les noms Docker
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb_guide:27017/")
ES_HOST = os.getenv("ES_HOST", "http://elasticsearch_guide:9200")

def get_db_clients():
    """Retourne les clients Mongo et Elastic prêts à l'emploi"""
    print(f"🔗 Connexion Mongo : {MONGO_URI}")
    print(f"🔗 Connexion Elastic : {ES_HOST}")
    
    mongo_client = MongoClient(MONGO_URI)
    # Pour ES 7.17, on passe l'hôte dans une liste
    es_client = Elasticsearch([ES_HOST])
    return mongo_client['guide_voyage'], es_client

def migrate_data():
    db, es = get_db_clients()
    
    # 1. Attente Elasticsearch (Boot check)
    print("⏳ Vérification de la disponibilité d'Elasticsearch...")
    for i in range(10):
        try:
            if es.ping():
                print("✅ Elasticsearch est en ligne !")
                break
        except Exception as e:
            pass
        print(f"   ... attente ({i+1}/10)")
        time.sleep(2)
    else:
        print("❌ Erreur : Impossible de joindre Elasticsearch sur localhost:9200")
        print("👉 Vérifie que ton conteneur 'elasticsearch_guide' est bien démarré (docker ps)")
        return

    # 2. Migration des Capitales
    print("📤 Migration des capitales...")
    villes = list(db['capitales'].find({}, {'_id': 0}))
    if villes:
        actions = []
        for v in villes:
            # On nettoie le nom de la capitale pour l'ID
            doc_id = v['capitale'].strip().lower().replace(" ", "_")
            actions.append({
                "_index": "capitales",
                "_id": doc_id,
                "_source": v
            })
        
        helpers.bulk(es, actions)
        print(f"✅ {len(villes)} villes synchronisées vers Elasticsearch.")
    else:
        print("⚠️ Aucune capitale trouvée dans MongoDB (collection 'capitales' vide).")

    # 3. Migration des Restaurants
    print("📤 Migration des restaurants...")
    restos = list(db['restaurants'].find({}, {'_id': 0}))
    if restos:
        actions = [{
            "_index": "restaurants",
            "_source": r
        } for r in restos]
        
        helpers.bulk(es, actions)
        print(f"✅ {len(restos)} restaurants synchronisés vers Elasticsearch.")
    else:
        print("⚠️ Aucun restaurant trouvé dans MongoDB (collection 'restaurants' vide).")

if __name__ == "__main__":
    print("============================================================")
    print("🚀 DÉMARRAGE DE LA SYNCHRONISATION MONGO -> ELASTIC")
    print("============================================================")
    migrate_data()
    print("============================================================")
    print("✨ Opération terminée !")