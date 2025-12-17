"""Test fonctionnel pour Dublin (Version 2025)"""
import scrapy
from scrapy.crawler import CrawlerProcess
import re

class TestDublinSpider(scrapy.Spider):
    name = 'test_dublin'
    start_urls = ['https://www.routard.com/fr/guide/europe/irlande/dublin']
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'ROBOTSTXT_OBEY': False,
        'LOG_LEVEL': 'INFO'
    }
    
    def parse(self, response):
        print("\n" + "="*80)
        print("🎯 TEST EXTRACTION DATA DUBLIN (V2025)")
        print("="*80)
        
        # 1. Extraction du script Next.js (Source réelle des données)
        scripts = response.xpath('//script[contains(text(), "resume")]/text()').getall()
        full_data_text = "".join(scripts)
        
        # 2. Localisation du champ "resume" qui contient le HTML des infos pratiques
        resume_match = re.search(r'"resume":"(.*?)"', full_data_text)
        
        if resume_match:
            # Décodage de l'unicode (\u003cp\u003e -> <p>)
            raw_html = resume_match.group(1).encode().decode('unicode-escape')
            # Nettoyage des balises HTML
            clean_text = re.sub(r'<[^>]+>', ' ', raw_html)
            
            print(f"✅ Bloc de données trouvé ({len(clean_text)} caractères)")

            # Extraction par patterns
            patterns = {
                "Meilleure saison": r'Meilleure saison\s*:\s*([^.]+)',
                "Décalage horaire": r'Décalage horaire\s*:\s*([^.]+)',
                "Durée de vol": r'Durée de vol direct[^:]*:\s*([^.]+)',
                "Papiers": r'Papiers\s*:\s*([^.]+)'
            }

            for label, pattern in patterns.items():
                match = re.search(pattern, clean_text, re.IGNORECASE)
                val = match.group(1).strip() if match else "❌ Non trouvé"
                print(f"👉 {label}: {val}")
        else:
            print("❌ Erreur : Impossible de trouver le bloc 'resume' dans les scripts.")

        # 3. Test de la description meta
        meta_desc = response.xpath('//meta[@name="description"]/@content').get()
        print(f"\n📝 META DESCRIPTION:\n{meta_desc}")

        print("\n" + "="*80)
        print("✅ TEST TERMINÉ")
        print("="*80)

if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(TestDublinSpider)
    process.start()