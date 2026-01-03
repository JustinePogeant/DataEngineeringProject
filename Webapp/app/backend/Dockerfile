FROM python:3.9-slim

WORKDIR /app

# Installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie de tout le code backend
COPY . .

# On lance la synchronisation (database.py) PUIS l'API (main.py)
# Note : database.py contient déjà la boucle d'attente pour Elasticsearch
CMD ["sh", "-c", "python database.py && python main.py"]