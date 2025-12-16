import json
from datetime import datetime


class RoutardPipeline:
    """
    Pipeline pour nettoyer et sauvegarder les données extraites
    par le spider EuropeanCapitalsSpider.
    """

    def open_spider(self, spider):
        """Initialisation à l’ouverture du spider"""
        # Fichier JSON pour stocker les données
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.file = open(f'european_capitals_{timestamp}.json', 'w', encoding='utf-8')
        self.file.write('[\n')  # Début de la liste JSON
        self.first_item = True

    def close_spider(self, spider):
        """Fermeture du fichier JSON"""
        self.file.write('\n]')
        self.file.close()
        spider.logger.info("Fichier JSON sauvegardé avec succès.")

    def process_item(self, item, spider):
        """Nettoyage et écriture de chaque item"""
        # Vérifier que c’est bien un CapitaleItem
        if isinstance(item, dict) or item.__class__.__name__ == 'CapitaleItem':
            # Nettoyage rapide
            for key in ['description', 'a_propos', 'meilleure_saison', 'quand_partir', 'decalage_horaire', 'duree_vol']:
                if key in item and item[key]:
                    item[key] = item[key].strip() if isinstance(item[key], str) else item[key]

            # Infos pratiques : assurer que c’est un dict
            if 'infos_pratiques' in item and not isinstance(item['infos_pratiques'], dict):
                item['infos_pratiques'] = dict(item['infos_pratiques']) if item['infos_pratiques'] else {}

            # Que voir : assurer que c’est une liste
            if 'que_voir' in item and not isinstance(item['que_voir'], list):
                item['que_voir'] = [item['que_voir']] if item['que_voir'] else []

            # Températures : dict vide si absent
            if 'temperatures' not in item or not item['temperatures']:
                item['temperatures'] = {}

            # Carte : None si absent
            if 'carte' not in item:
                item['carte'] = None

            # Sauvegarde JSON
            json_str = json.dumps(dict(item), ensure_ascii=False, indent=2)
            if not self.first_item:
                self.file.write(',\n')
            self.file.write(json_str)
            self.first_item = False

        return item
