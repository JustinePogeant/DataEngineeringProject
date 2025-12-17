import scrapy
import re
import html
from datetime import datetime

class EuropeanCapitalsSpider(scrapy.Spider):
    name = 'european_capitals'
    
    # Ajoute ici toutes tes URLs
    start_urls = [
        'https://www.routard.com/fr/guide/europe/irlande/dublin',
        'https://www.routard.com/fr/guide/europe/italie/rome',
        'https://www.routard.com/fr/guide/europe/france/paris',
        'https://www.routard.com/fr/guide/europe/espagne/madrid',
        'https://www.routard.com/fr/guide/europe/allemagne/berlin',
        'https://www.routard.com/fr/guide/europe/portugal/lisbonne',
        'https://www.routard.com/fr/guide/europe/pays_bas/amsterdam',
        'https://www.routard.com/fr/guide/europe/belgique/bruxelles',
        'https://www.routard.com/fr/guide/europe/autriche/vienne',
        'https://www.routard.com/fr/guide/europe/suede/stockholm',
        'https://www.routard.com/fr/guide/europe/danemark/copenhague',
        'https://www.routard.com/fr/guide/europe/finlande/helsinki',
        'https://www.routard.com/fr/guide/europe/pologne/varsovie',
        'https://www.routard.com/fr/guide/europe/republique_tcheque/prague',
        'https://www.routard.com/fr/guide/europe/hongrie/budapest',
        'https://www.routard.com/fr/guide/europe/grece/athenes',
        'https://www.routard.com/fr/guide/europe/croatie/zagreb',
        'https://www.routard.com/fr/guide/europe/bulgarie/sofia',
        'https://www.routard.com/fr/guide/europe/roumanie/bucarest',
        'https://www.routard.com/fr/guide/europe/slovaquie/bratislava',
        'https://www.routard.com/fr/guide/europe/slovenie/ljubljana',
        'https://www.routard.com/fr/guide/europe/estonie/tallinn',
        'https://www.routard.com/fr/guide/europe/lettonie/riga',
        'https://www.routard.com/fr/guide/europe/lituanie/vilnius',
        'https://www.routard.com/fr/guide/europe/chypre/nicosie',
        'https://www.routard.com/fr/guide/europe/malte/valette',
        'https://www.routard.com/fr/guide/europe/islande/reykjavik',
    ]

    def parse(self, response):
        # Nettoyage du nom de la capitale (enlève "Voyage ")
        raw_title = response.xpath('//h1/text()').get() or "Dublin"
        capitale = raw_title.replace("Voyage ", "").strip()
        
        script_content = "".join(response.xpath('//script//text()').getall())
        
        # 1. Récupération des paragraphes
        all_paragraphs = re.findall(r'\\u003cp\\u003e(.*?)\\u003c/p\\u003e', script_content)
        
        description_parts = []
        quand = "Non spécifié"
        decalage = "Non spécifié"
        
        for p in all_paragraphs:
            clean_p = self.deep_clean(p)
            
            # Extraction Meilleure saison
            if "Meilleure saison :" in clean_p:
                match = re.search(r'Meilleure saison\s*:\s*(.*?)(?:\.|\-|Durée|$)', clean_p)
                if match: quand = match.group(1).strip()
                
            # Extraction Décalage
            if "Décalage horaire :" in clean_p:
                match = re.search(r'Décalage horaire\s*:\s*(.*?)(?:\.|$)', clean_p)
                if match: decalage = match.group(1).strip()
            
            # Construction de la description (paragraphes longs uniquement)
            if len(clean_p) > 100 and "Papiers :" not in clean_p:
                if clean_p not in description_parts:
                    description_parts.append(clean_p)

        yield {
            "capitale": capitale,
            "description": " ".join(description_parts[:2]),
            "quand_partir": quand,
            "decalage": decalage,
            "url": response.url,
            "date_scraping": datetime.now().strftime("%d/%m/%Y")
        }

    def deep_clean(self, text):
        if not text: return ""
        try:
            # Réparation de l'encodage
            text = text.encode('utf-8').decode('unicode_escape')
            text = text.encode('latin-1', errors='ignore').decode('utf-8', errors='ignore')
            # Nettoyage HTML
            text = re.sub(r'<.*?>', '', text)
            text = html.unescape(text)
            # Corrections spécifiques finales
            text = text.replace('â', "'") # Pour les apostrophes
            text = text.replace("ch'teau", "château") # Correction manuelle du bug restant
            return text.strip()
        except:
            return text