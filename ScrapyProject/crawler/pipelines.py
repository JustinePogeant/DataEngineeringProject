import json
import re
from datetime import datetime

class RoutardPipeline:
    def open_spider(self, spider):
        self.file = open('data_capitale_complete.json', 'w', encoding='utf-8')
        self.file.write('[\n')
        self.first_item = True

    def close_spider(self, spider):
        self.file.write('\n]')
        self.file.close()

    def process_item(self, item, spider):
        # Nettoyage final
        if isinstance(item.get('que_voir'), list):
            item['que_voir'] = list(set(item['que_voir'])) # Déduplication
        
        # Conversion en JSON
        line = json.dumps(dict(item), ensure_ascii=False, indent=4)
        
        if not self.first_item:
            self.file.write(',\n')
        
        self.file.write(line)
        self.first_item = False
        return item
    
    def clean_description(self, text):
        if not text:
            return "Description non disponible"
        # Supprime les caractères non-ASCII ou bizarres
        # Cette regex ne garde que les caractères alphanumériques et la ponctuation standard
        cleaned = re.sub(r'[^\x20-\x7E\u00C0-\u00FF]+', ' ', text)
        return cleaned.strip()