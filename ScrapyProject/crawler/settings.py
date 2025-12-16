BOT_NAME = "crawler"

# Déclare où Scrapy doit chercher les modules de spiders
SPIDER_MODULES = ["crawler.spiders"]

# Déclare le module par défaut pour la création de nouveaux spiders
NEWSPIDER_MODULE = "crawler.spiders"


ITEM_PIPELINES = {
    'crawler.pipelines.RoutardPipeline': 300,
}