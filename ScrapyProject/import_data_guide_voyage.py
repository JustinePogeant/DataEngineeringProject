#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour importer vos données JSON scrappées dans MongoDB
Usage: python import_data.py restaurant restaurants.json
       python import_data.py capitale capitales.json
"""

from pymongo import MongoClient
from datetime import datetime
import json
import os
import sys


class MongoDBImporter:
    """Classe pour importer des données JSON dans MongoDB"""
    
    def __init__(self, mongo_uri='mongodb://mongodb_guide:27017/', database='guide_voyage'):
        print(f"🔗 Connexion à MongoDB...")
        self.client = MongoClient(mongo_uri)
        self.db = self.client[database]
        self.capitales = self.db['capitales']
        self.restaurants = self.db['restaurants']
        self.stats = {
            'capitales_inserted': 0,
            'capitales_updated': 0,
            'restaurants_inserted': 0,
            'restaurants_updated': 0,
            'errors': 0
        }
        self._create_indexes()
    
    def _create_indexes(self):
        """Crée les index nécessaires"""
        print("📇 Création des index...")
        # Index capitales
        self.capitales.create_index('capitale', unique=True)
        self.capitales.create_index('date_scraping')
        
        # Index restaurants
        self.restaurants.create_index([('nom', 1), ('capitale', 1)], unique=True)
        self.restaurants.create_index('capitale')
        self.restaurants.create_index('type_cuisine')
        self.restaurants.create_index('prix_niveau')
        self.restaurants.create_index('date_scraping')
        
        print("✅ Index créés\n")
    
    def import_capitales_from_json(self, json_file):
        """Importe les capitales depuis un fichier JSON"""
        print(f"📍 Import des capitales depuis {json_file}...")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Si c'est un seul objet, le met dans une liste
            if isinstance(data, dict):
                data = [data]
            
            for item in data:
                self._insert_capitale(item)
            
            print(f"\n✅ Import terminé: {self.stats['capitales_inserted']} insérées, "
                  f"{self.stats['capitales_updated']} mises à jour")
            
        except FileNotFoundError:
            print(f"❌ Fichier non trouvé: {json_file}")
            print(f"💡 Vérifiez que le fichier existe dans le dossier actuel")
        except json.JSONDecodeError as e:
            print(f"❌ Erreur JSON: {e}")
            print(f"💡 Vérifiez que votre fichier JSON est valide")
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    def import_restaurants_from_json(self, json_file):
        """Importe les restaurants depuis un fichier JSON"""
        print(f"🍽️  Import des restaurants depuis {json_file}...")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Si c'est un seul objet, le met dans une liste
            if isinstance(data, dict):
                data = [data]
            
            for item in data:
                self._insert_restaurant(item)
            
            print(f"\n✅ Import terminé: {self.stats['restaurants_inserted']} insérés, "
                  f"{self.stats['restaurants_updated']} mis à jour")
            
        except FileNotFoundError:
            print(f"❌ Fichier non trouvé: {json_file}")
            print(f"💡 Vérifiez que le fichier existe dans le dossier actuel")
        except json.JSONDecodeError as e:
            print(f"❌ Erreur JSON: {e}")
            print(f"💡 Vérifiez que votre fichier JSON est valide")
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    def _insert_capitale(self, item):
        """Insère ou met à jour une capitale"""
        try:
            # Nettoyage
            clean_item = self._clean_capitale(item)
            
            if not clean_item.get('capitale'):
                print(f"  ⚠️  Capitale sans nom, ignorée")
                self.stats['errors'] += 1
                return
            
            # Upsert (insert ou update)
            result = self.capitales.update_one(
                {'capitale': clean_item['capitale']},
                {'$set': clean_item},
                upsert=True
            )
            
            if result.upserted_id:
                self.stats['capitales_inserted'] += 1
                print(f"  ✅ {clean_item['capitale']}")
            elif result.modified_count > 0:
                self.stats['capitales_updated'] += 1
                print(f"  🔄 {clean_item['capitale']} (mise à jour)")
            else:
                print(f"  ℹ️  {clean_item['capitale']} (déjà à jour)")
            
        except Exception as e:
            self.stats['errors'] += 1
            print(f"  ❌ Erreur: {e}")
    
    def _insert_restaurant(self, item):
        """Insère ou met à jour un restaurant"""
        try:
            # Nettoyage
            clean_item = self._clean_restaurant(item)
            
            if not clean_item.get('nom') or not clean_item.get('capitale'):
                print(f"  ⚠️  Restaurant sans nom ou capitale, ignoré")
                self.stats['errors'] += 1
                return
            
            # Upsert (insert ou update)
            result = self.restaurants.update_one(
                {'nom': clean_item['nom'], 'capitale': clean_item['capitale']},
                {'$set': clean_item},
                upsert=True
            )
            
            if result.upserted_id:
                self.stats['restaurants_inserted'] += 1
                print(f"  ✅ {clean_item['nom']} ({clean_item['capitale']})")
            elif result.modified_count > 0:
                self.stats['restaurants_updated'] += 1
                print(f"  🔄 {clean_item['nom']} ({clean_item['capitale']}) (mise à jour)")
            else:
                print(f"  ℹ️  {clean_item['nom']} ({clean_item['capitale']}) (déjà à jour)")
            
        except Exception as e:
            self.stats['errors'] += 1
            print(f"  ❌ Erreur: {e}")
    
    def _clean_capitale(self, item):
        """Nettoie les données d'une capitale"""
        clean = {}
        
        if 'capitale' in item:
            clean['capitale'] = str(item['capitale']).strip()
        
        if 'description' in item and item['description']:
            clean['description'] = str(item['description']).strip()
        
        if 'quand_partir' in item and item['quand_partir']:
            clean['quand_partir'] = str(item['quand_partir']).strip()
        
        if 'decalage' in item and item['decalage']:
            clean['decalage'] = str(item['decalage']).strip()
        
        if 'url' in item and item['url']:
            clean['url'] = str(item['url']).strip()
        
        clean['date_scraping'] = item.get('date_scraping', datetime.now().strftime("%d/%m/%Y"))
        clean['last_updated'] = datetime.now()
        
        # Supprime les valeurs None ou vides
        clean = {k: v for k, v in clean.items() if v not in [None, '', 'null']}
        
        return clean
    
    def _clean_restaurant(self, item):
        """Nettoie les données d'un restaurant"""
        clean = {}
        
        if 'nom' in item:
            clean['nom'] = str(item['nom']).strip()
        
        if 'capitale' in item:
            clean['capitale'] = str(item['capitale']).strip()
        
        if 'adresse' in item and item['adresse']:
            clean['adresse'] = str(item['adresse']).strip()
        
        if 'type_cuisine' in item and item['type_cuisine'] not in ['null', None]:
            clean['type_cuisine'] = str(item['type_cuisine']).strip()
        
        if 'description' in item and item['description']:
            clean['description'] = str(item['description']).strip()
        
        # Prix
        if 'prix_niveau' in item:
            prix = item['prix_niveau']
            if isinstance(prix, str) and prix != 'null':
                clean['prix_niveau'] = prix.count('€')
            elif isinstance(prix, int):
                clean['prix_niveau'] = prix
        
        if 'telephone' in item and item['telephone']:
            clean['telephone'] = str(item['telephone']).strip()
        
        if 'site_web' in item and item['site_web']:
            clean['site_web'] = str(item['site_web']).strip()
        
        # Images
        if 'images' in item and item['images']:
            if isinstance(item['images'], list):
                clean['images'] = [img.strip() for img in item['images'] if img]
            else:
                clean['images'] = [str(item['images']).strip()]
        
        if 'url' in item and item['url']:
            clean['url'] = str(item['url']).strip()
        
        clean['date_scraping'] = item.get('date_scraping', datetime.now().isoformat())
        clean['last_updated'] = datetime.now()
        
        # Supprime les valeurs None ou vides
        clean = {k: v for k, v in clean.items() if v not in [None, '', 'null', []]}
        
        return clean
    
    def display_stats(self):
        """Affiche les statistiques finales"""
        print("\n" + "=" * 60)
        print("📊 STATISTIQUES D'IMPORT")
        print("=" * 60)
        print(f"Capitales:")
        print(f"  - Insérées: {self.stats['capitales_inserted']}")
        print(f"  - Mises à jour: {self.stats['capitales_updated']}")
        print(f"\nRestaurants:")
        print(f"  - Insérés: {self.stats['restaurants_inserted']}")
        print(f"  - Mis à jour: {self.stats['restaurants_updated']}")
        print(f"\nErreurs: {self.stats['errors']}")
        print("=" * 60)
    
    def close(self):
        """Ferme la connexion"""
        self.client.close()


def main():
    """Fonction principale"""
    print("=" * 60)
    print("🌍 IMPORT DONNÉES JSON VERS MONGODB")
    print("=" * 60)
    print()
    
    # Vérification des arguments
    if len(sys.argv) < 3:
        print("📖 Comment utiliser ce script:")
        print()
        print("  python import_data.py <type> <fichier.json>")
        print()
        print("  <type> peut être:")
        print("    - capitale   (pour importer des capitales)")
        print("    - restaurant (pour importer des restaurants)")
        print()
        print("  <fichier.json> est le chemin vers votre fichier")
        print()
        print("💡 Exemples:")
        print("  python import_data.py capitale capitales.json")
        print("  python import_data.py restaurant restaurants.json")
        print("  python import_data.py restaurant C:/Users/vous/data/restos.json")
        print()
        sys.exit(1)
    
    data_type = sys.argv[1].lower()
    json_file = sys.argv[2]
    
    # Vérification du type
    if data_type not in ['capitale', 'restaurant']:
        print("❌ Type invalide. Utilisez 'capitale' ou 'restaurant'")
        sys.exit(1)
    
    # Vérification du fichier
    if not os.path.exists(json_file):
        print(f"❌ Fichier non trouvé: {json_file}")
        print(f"💡 Dossier actuel: {os.getcwd()}")
        print(f"💡 Fichiers disponibles: {os.listdir('.')}")
        sys.exit(1)
    
    # Import
    try:
        importer = MongoDBImporter()
        
        if data_type == 'capitale':
            importer.import_capitales_from_json(json_file)
        else:
            importer.import_restaurants_from_json(json_file)
        
        importer.display_stats()
        importer.close()
        
        print("\n✅ Import terminé avec succès!")
        print("\n💡 Vérifiez vos données avec mongosh:")
        print("   mongosh 'mongodb://localhost:27017'")
        print("   use guide_voyage")
        if data_type == 'capitale':
            print("   db.capitales.countDocuments()")
            print("   db.capitales.find().pretty()")
        else:
            print("   db.restaurants.countDocuments()")
            print("   db.restaurants.find().pretty()")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()