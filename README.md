*Projet réalisé par Justine Pogeant et Lina Ouchaou - Data Engineering - 2025-2026*

# Guide de Voyage Intelligent : Pipeline Data Engineering End-to-End

## Table des Matières
1. [Vue d'ensemble du projet](#-vue-densemble-du-projet)
2. [Architecture technique](#-architecture-technique)
3. [Structure des Fichiers](#-structure-des-fichiers)
4. [Installation et déploiement](#-installation-et-déploiement)
5. [Fonctionnement du Système](#-fonctionnement-du-système)
6. [Détails du Pipeline ETL](#-détails-du-pipeline-etl)
7. [Configuration du Moteur de Recherche](#-configuration-du-moteur-de-recherche)
8. [Défis techniques et solutions](#-défis-techniques-et-solutions)
9. [Maintenance et commandes utiles](#-maintenance-et-commandes-utiles)
10. [Conclusion](#-conclusion)

---

## Vue d'ensemble du projet

### ### Objectifs & Vision
L'objectif est de concevoir une plateforme capable d'agréger, de traiter et de restituer des données de voyage de manière optimale. Ce projet démontre la mise en place d'un pipeline **ETL** (Extract, Transform, Load) moderne et automatisé.

**Cas d'usage :** Un voyageur souhaite découvrir les capitales européennes tout en trouvant les meilleures adresses gastronomiques (**Guide Michelin**) à proximité.

### ### Fonctionnalités clés
*  **Scraping automatique** : Récupération des données capitales (Routard) et restaurants (Michelin).
*  **Stockage Hybride** : MongoDB pour la persistance et Elasticsearch pour la recherche "Fuzzy".
*  **Recherche Avancée** : Moteur de recherche plein texte (par ville, type de cuisine, etc.).
*  **Interface Web** : Visualisation dynamique sous Vue.js avec cartographie intégrée.
*  **Architecture Docker** : 5 micro-services isolés et orchestrés.

---

##  Architecture Technique

### ### Stack Technologique
|     Composant     |    Technologie    |                   Justification                                         |
| --------------------------------------------------------------------------------------------------------------- |
| **Scraping**      | **Scrapy**        | Gestion asynchrone permettant de scraper plusieurs villes en parallèle. |
| **Database**      | **MongoDB**       | Flexibilité du format JSON pour des données hétérogènes.                |
| **Search Engine** | **Elasticsearch** | Moteur de recherche plein texte performant.                             |
| **Backend**       | **Flask**         | API légère et robuste pour distribuer les données.                      |
| **Frontend**      | **Vue.js**        | Interface réactive pour une expérience utilisateur fluide.              |

---

##  Structure des Fichiers

L'organisation du projet suit une logique de séparation des préoccupations par service :

```text
.
├── backend/                # API Flask
│   ├── app.py              # Points d'entrée de l'API
│   └── requirements.txt    # Dépendances Python (Flask, PyMongo, Elasticsearch)
├── frontend/               # Application Vue.js
│   ├── src/                # Composants et logique Vue
│   └── package.json        # Dépendances JS
├── scraping/               # Projets Scrapy
│   ├── michelin/           # Spider pour les restaurants
│   └── routard/            # Spider pour les capitales
├── workers/                # Scripts d'importation et d'automatisation
│   ├── import_data.py      # Script principal d'ingestion ETL
│   └── import_data.sh      # Script de contrôle (Bash)
├── docker-compose.yml      # Orchestration des services
└── .gitignore              # Exclusion des fichiers inutiles
```

## Installation et Déploiement

### 1. Préparation de l'environnement
Ouvrez votre terminal (PowerShell ou Bash) et préparez le projet :

# Cloner le dépôt
git clone https://github.com/JustinePogeant/DataEngineeringProject.git
cd DataEngineeringProject

# Configuration de Git pour éviter les erreurs de fin de ligne (Windows)
git config core.autocrlf false

### 2. Lancement via Docker Compose
Une seule commande suffit pour construire les images et démarrer toute l'infrastructure : 'PowerShell'


# Construire et lancer les conteneurs
docker-compose up --build
Sortie attendue du terminal :

[+] Running 5/5
 ✔ Container mongodb_guide        Healthy
 ✔ Container elasticsearch_guide  Healthy
 ✔ Container flask_backend        Started
 ✔ Container vue_frontend         Started
 ✔ Container data_import_worker   Exited (0)  <-- Importation terminée avec succès !
 
 
 ## Fonctionnement du Système
### Flux de données nominal

Extraction : Les spiders Scrapy parcourent les sites cibles et génèrent des fichiers JSON structurés.

Orchestration : Docker Compose lance les bases de données, puis le data_import_worker.

Ingestion : Le worker lit les JSON, nettoie les données et les injecte dans MongoDB et Elasticsearch via des scripts Python.

Consommation : L'API Flask interroge Elasticsearch pour les recherches textuelles et MongoDB pour les détails complets, puis sert le Frontend Vue.js.

## Détails du Pipeline ETL

### Extraction (Scrapy)

Le spider extrait les données et les formate en objets structurés avant exportation en JSON.

# Exemple d'extraction dans le spider Michelin
``` code
def parse_restaurant(self, response):
    yield {
        'nom': response.css('h1.restaurant-details__name::text').get().strip(),
        'cuisine': response.css('span.restaurant-details__cuisine::text').get(),
        'ville': response.meta['city'],
        'coordonnees': {
            'lat': response.css('meta[property="restaurant:location:latitude"]::attr(content)').get(),
            'lon': response.css('meta[property="restaurant:location:longitude"]::attr(content)').get()
        }
    }
```

## Configuration du Moteur de Recherche

Elasticsearch est utilisé pour fournir une recherche flexible ("fuzzy search"). Voici la configuration appliquée lors de l'ingestion :

### Indexation des données
Nous créons un index restaurants avec un mapping spécifique pour optimiser les recherches sur le nom et le type de cuisine.

# Exemple de configuration de l'index dans le worker d'importation
``` code
mapping = {
    "mappings": {
        "properties": {
            "nom": {"type": "text", "analyzer": "french"},
            "cuisine": {"type": "keyword"},
            "ville": {"type": "keyword"}
        }
    }
}
es.indices.create(index='restaurants', body=mapping, ignore=400)
```

### Logique de Recherche

L'API Flask utilise des requêtes multi_match pour permettre à l'utilisateur de trouver un restaurant même avec une faute de frappe.

Défis Techniques et Solutions

### 1. Synchronisation des services (Race Condition)
Problème : Le script d'importation échouait car il tentait de se connecter à MongoDB avant son démarrage complet. 
Solution : Utilisation d'une boucle d'attente active (wait-for-it) dans un script import_data.sh.

``` code
#!/bin/bash
echo " Attente de la base de données MongoDB..."
while ! nc -z mongodb_guide 27017; do
  sleep 1
done
echo " MongoDB est prêt ! Lancement de l'importation..."
python import_data_guide_voyage.py
```

## Maintenance et Commandes Utiles
### Vérifier les logs

docker-compose logs -f data_import_worker

### Explorer MongoDB
# Entrer dans le shell MongoDB
docker exec -it mongodb_guide mongosh

# Commandes utiles
use guide_db
db.restaurants.countDocuments()
db.restaurants.findOne({ville: "Paris"})

### Réinitialiser proprement le projet
# Supprimer les conteneurs et les volumes (efface les données)
docker-compose down -v


## Conclusion

Ce projet a permis de mettre en place une architecture Data Engineering complète, allant de la collecte de données non structurées sur le web jusqu'à leur mise à disposition via une webapp claire et facile d'utilisation. L'utilisation de Docker garantit la reproductibilité de l'environnement, tandis que le couplage de MongoDB et Elasticsearch offre un équilibre parfait entre flexibilité de stockage et performance de recherche. Ce pipeline constitue une base solide pour l'ajout futur de nouvelles sources de données ou l'implémentation d'analyses prédictives sur les flux touristiques.

*Projet réalisé par Justine Pogeant et Lina Ouchaou - Data Engineering - 2025-2026*