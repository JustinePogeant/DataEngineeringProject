FROM python:3.9-slim

# Installation de netcat pour le test de connexion
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# On copie tout le dossier (le script py, le script sh et les JSON)
COPY . .

# Installation de la seule dépendance nécessaire
RUN pip install pymongo

# Rendre le script bash exécutable
RUN chmod +x import_data.sh

# Commande de lancement
CMD ["./import_data.sh"]