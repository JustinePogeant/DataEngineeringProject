#!/bin/bash
echo "⏳ Attente de MongoDB..."
while ! nc -z mongodb_guide 27017; do   
  sleep 1
done

echo "✅ MongoDB est prêt, lancement de l'importation..."

# Remplace le nom du script .py si nécessaire
python import_data_guide_voyage.py capitale capitals_2025-12-17T10-00-18+00-00.json
python import_data_guide_voyage.py restaurant michelin_restaurants.json

echo "✨ Importation terminée avec succès !"