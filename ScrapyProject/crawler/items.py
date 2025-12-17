import scrapy

class CapitaleItem(scrapy.Item):
    """Item représentant une capitale européenne avec toutes les rubriques du Routard"""
    
    # Informations principales
    capitale = scrapy.Field()
    pays = scrapy.Field()
    url = scrapy.Field()
    description = scrapy.Field()
    a_propos = scrapy.Field()
    
    # Informations voyage & climat
    meilleure_saison = scrapy.Field()
    quand_partir = scrapy.Field()
    decalage_horaire = scrapy.Field()
    duree_vol = scrapy.Field()
    temperatures = scrapy.Field()  # Dict mois -> températures
    
    # Informations pratiques et culturelles
    # Contiendra le dictionnaire extrait dans parse_infos
    infos_pratiques = scrapy.Field()  
    
    # Attractions et médias
    que_voir = scrapy.Field()  # Liste des attractions (Incontournables)
    carte = scrapy.Field()     # URL de la carte
    
    # Métadonnées techniques
    date_scraping = scrapy.Field()
    source = scrapy.Field()

# Les autres items peuvent rester pour d'autres types de scraping
class DestinationItem(scrapy.Item):
    """Item représentant une destination du Guide du Routard"""
    
    nom = scrapy.Field()
    continent = scrapy.Field()
    url = scrapy.Field()
    description = scrapy.Field()
    
    conseils_pratiques = scrapy.Field()
    budget_moyen = scrapy.Field()
    climat = scrapy.Field()
    meilleure_periode = scrapy.Field()
    
    langues = scrapy.Field()
    monnaie = scrapy.Field()
    
    attractions = scrapy.Field()
    
    date_scraping = scrapy.Field()
    source = scrapy.Field()


class ArticleItem(scrapy.Item):
    """Item pour les articles de blog/conseils"""
    
    titre = scrapy.Field()
    auteur = scrapy.Field()
    date_publication = scrapy.Field()
    contenu = scrapy.Field()
    categorie = scrapy.Field()
    destination_liee = scrapy.Field()
    url = scrapy.Field()
    tags = scrapy.Field()
    date_scraping = scrapy.Field()


class AvisItem(scrapy.Item):
    """Item pour les avis utilisateurs"""
    
    destination = scrapy.Field()
    note = scrapy.Field()
    titre_avis = scrapy.Field()
    commentaire = scrapy.Field()
    auteur = scrapy.Field()
    date_visite = scrapy.Field()
    date_avis = scrapy.Field()
    url = scrapy.Field()
    date_scraping = scrapy.Field()
