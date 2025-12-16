import scrapy
from datetime import datetime
import re
import json


class EuropeanCapitalsSpider(scrapy.Spider):
    """
    Spider pour scraper les informations des capitales européennes
    sur le Guide du Routard
    """
    name = 'european_capitals'
    allowed_domains = ['routard.com']
    
    # Liste des capitales européennes avec leurs URLs
    EUROPEAN_CAPITALS = {
        'Dublin': 'https://www.routard.com/guide/code_dest/dublin.htm',
        'Paris': 'https://www.routard.com/guide/code_dest/paris.htm',
        'Londres': 'https://www.routard.com/guide/code_dest/londres.htm',
        'Berlin': 'https://www.routard.com/guide/code_dest/berlin.htm',
        'Madrid': 'https://www.routard.com/guide/code_dest/madrid.htm',
        'Rome': 'https://www.routard.com/guide/code_dest/rome.htm',
        'Lisbonne': 'https://www.routard.com/guide/code_dest/lisbonne.htm',
        'Amsterdam': 'https://www.routard.com/guide/code_dest/amsterdam.htm',
        'Bruxelles': 'https://www.routard.com/guide/code_dest/bruxelles.htm',
        'Vienne': 'https://www.routard.com/guide/code_dest/vienne.htm',
        'Prague': 'https://www.routard.com/guide/code_dest/prague.htm',
        'Budapest': 'https://www.routard.com/guide/code_dest/budapest.htm',
        'Varsovie': 'https://www.routard.com/guide/code_dest/varsovie.htm',
        'Copenhague': 'https://www.routard.com/guide/code_dest/copenhague.htm',
        'Stockholm': 'https://www.routard.com/guide/code_dest/stockholm.htm',
        'Helsinki': 'https://www.routard.com/guide/code_dest/helsinki.htm',
        'Oslo': 'https://www.routard.com/guide/code_dest/oslo.htm',
        'Athènes': 'https://www.routard.com/guide/code_dest/athenes.htm',
        'Bucarest': 'https://www.routard.com/guide/code_dest/bucarest.htm',
        'Sofia': 'https://www.routard.com/guide/code_dest/sofia.htm',
        'Belgrade': 'https://www.routard.com/guide/code_dest/belgrade.htm',
        'Zagreb': 'https://www.routard.com/guide/code_dest/zagreb.htm',
        'Ljubljana': 'https://www.routard.com/guide/code_dest/ljubljana.htm',
        'Bratislava': 'https://www.routard.com/guide/code_dest/bratislava.htm',
        'Tallinn': 'https://www.routard.com/guide/code_dest/tallinn.htm',
        'Riga': 'https://www.routard.com/guide/code_dest/riga.htm',
        'Vilnius': 'https://www.routard.com/guide/code_dest/vilnius.htm',
        'Luxembourg': 'https://www.routard.com/guide/code_dest/luxembourg.htm',
        'Monaco': 'https://www.routard.com/guide/code_dest/monaco.htm',
        'Reykjavik': 'https://www.routard.com/guide/code_dest/reykjavik.htm',
    }
    
    custom_settings = {
        'DOWNLOAD_DELAY': 3,  # 3 secondes entre chaque requête
        'CONCURRENT_REQUESTS': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.routard.com/',
        },
        'RETRY_TIMES': 5,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429, 403],
        'DOWNLOAD_TIMEOUT': 30,
    }
    
    def start_requests(self):
        """Génère les requêtes pour toutes les capitales"""
        for capitale, url in self.EUROPEAN_CAPITALS.items():
            self.logger.info(f"Scraping capitale: {capitale}")
            yield scrapy.Request(
                url=url,
                callback=self.parse_capitale,
                meta={
                    'capitale': capitale,
                    'dont_redirect': False,
                    'handle_httpstatus_list': [301, 302, 403, 404]
                },
                errback=self.handle_error,
                dont_filter=True
            )
    
    def parse_capitale(self, response):
        """Parse la page d'une capitale"""
        capitale = response.meta['capitale']
        
        # Vérifier les erreurs HTTP
        if response.status in [403, 404]:
            self.logger.warning(f"Erreur {response.status} pour {capitale}: {response.url}")
            return
        
        self.logger.info(f"Parsing {capitale}: {response.url}")
        
        # Extraction des données principales
        data = {
            'capitale': capitale,
            'pays': self.extract_pays(response),
            'url': response.url,
            'description': self.extract_description(response),
            'a_propos': self.extract_a_propos(response),
            'meilleure_saison': self.extract_meilleure_saison(response),
            'quand_partir': self.extract_quand_partir(response),
            'decalage_horaire': self.extract_decalage_horaire(response),
            'duree_vol': self.extract_duree_vol(response),
            'temperatures': self.extract_temperatures(response),
            'carte': self.extract_carte(response),
            'infos_pratiques': self.extract_infos_pratiques(response),
            'que_voir': self.extract_que_voir(response),
            'date_scraping': datetime.now().isoformat(),
            'source': 'Guide du Routard'
        }
        
        self.logger.info(f"✓ Données extraites pour {capitale}")
        yield data
    
    def extract_pays(self, response):
        """Extrait le nom du pays"""
        # Essayer plusieurs sélecteurs
        pays = response.css('.breadcrumb a::text').getall()
        if len(pays) >= 2:
            return self.clean_text(pays[-2])
        
        # Alternative avec le titre
        titre = response.css('h1::text').get()
        if titre and ',' in titre:
            return self.clean_text(titre.split(',')[-1])
        
        return "Non spécifié"
    
    def extract_description(self, response):
        """Extrait la description principale"""
        # Plusieurs sélecteurs possibles
        selectors = [
            '.description p::text',
            '.intro-text p::text',
            '.chapo::text',
            'div[itemprop="description"]::text',
            '.content-intro p::text',
            'article p:first-of-type::text',
        ]
        
        for selector in selectors:
            description = response.css(selector).getall()
            if description:
                return self.clean_text(' '.join(description))
        
        # Fallback : prendre les premiers paragraphes
        all_paragraphs = response.css('p::text').getall()
        if all_paragraphs:
            return self.clean_text(' '.join(all_paragraphs[:3]))
        
        return "Description non disponible"
    
    def extract_a_propos(self, response):
        """Extrait la section 'À propos'"""
        # Chercher une section spécifique
        selectors = [
            '#a-propos *::text',
            '.about-section *::text',
            'section[class*="about"] *::text',
        ]
        
        for selector in selectors:
            textes = response.css(selector).getall()
            if textes:
                return self.clean_text(' '.join(textes))
        
        return None
    
    def extract_meilleure_saison(self, response):
        """Extrait la meilleure saison pour visiter"""
        # Chercher dans le texte
        text_content = response.css('body').get() or ''
        
        patterns = [
            r'meilleure(?:\s+période|\s+saison)[^\.:]*[:\.]\s*([^\.\n]+)',
            r'quand\s+partir[^\.:]*[:\.]\s*([^\.\n]+)',
            r'période\s+idéale[^\.:]*[:\.]\s*([^\.\n]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                return self.clean_text(match.group(1))
        
        # Chercher les mois mentionnés
        mois = self.extract_months_from_text(text_content)
        if mois:
            return ', '.join(mois)
        
        return "Non spécifié"
    
    def extract_quand_partir(self, response):
        """Extrait les informations 'Quand partir'"""
        selectors = [
            '#quand-partir *::text',
            '.when-to-go *::text',
            'section[class*="quand"] *::text',
        ]
        
        for selector in selectors:
            textes = response.css(selector).getall()
            if textes:
                return self.clean_text(' '.join(textes))
        
        return None
    
    def extract_decalage_horaire(self, response):
        """Extrait le décalage horaire"""
        text = response.css('body').get() or ''
        
        patterns = [
            r'décalage\s+horaire[^\.:]*[:\.]\s*([^\.\n]+)',
            r'fuseau\s+horaire[^\.:]*[:\.]\s*([^\.\n]+)',
            r'GMT\s*[+\-]\s*\d+',
            r'UTC\s*[+\-]\s*\d+',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self.clean_text(match.group(0))
        
        return "Non spécifié"
    
    def extract_duree_vol(self, response):
        """Extrait la durée de vol depuis Paris"""
        text = response.css('body').get() or ''
        
        patterns = [
            r'durée\s+(?:de\s+)?vol[^\.:]*[:\.]\s*([^\.\n]+)',
            r'temps\s+de\s+vol[^\.:]*[:\.]\s*([^\.\n]+)',
            r'(\d+h?\s*\d*)\s*(?:de\s+vol|en\s+avion)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self.clean_text(match.group(1) if match.lastindex else match.group(0))
        
        return "Non spécifié"
    
    def extract_temperatures(self, response):
        """Extrait les informations de température"""
        # Chercher un tableau de températures
        temp_data = {}
        
        # Sélecteurs pour tableaux météo
        rows = response.css('table.meteo tr, table.climat tr, .weather-table tr')
        
        for row in rows:
            mois = row.css('th::text, td:first-child::text').get()
            temp = row.css('td::text').getall()
            if mois and temp:
                temp_data[self.clean_text(mois)] = [self.clean_text(t) for t in temp]
        
        return temp_data if temp_data else None
    
    def extract_carte(self, response):
        """Extrait l'URL de la carte"""
        # Chercher les images de carte
        selectors = [
            'img[alt*="carte"]::attr(src)',
            'img[alt*="map"]::attr(src)',
            '.map img::attr(src)',
            '#map img::attr(src)',
        ]
        
        for selector in selectors:
            carte_url = response.css(selector).get()
            if carte_url:
                return response.urljoin(carte_url)
        
        # Chercher un iframe Google Maps
        iframe = response.css('iframe[src*="google.com/maps"]::attr(src)').get()
        if iframe:
            return iframe
        
        return None
    
    def extract_infos_pratiques(self, response):
        """Extrait les informations pratiques"""
        infos = {}
        
        # Liste des infos à chercher
        info_types = {
            'monnaie': r'monnaie[^\.:]*[:\.]\s*([^\.\n]+)',
            'langue': r'langue[^\.:]*[:\.]\s*([^\.\n]+)',
            'visa': r'visa[^\.:]*[:\.]\s*([^\.\n]+)',
            'electricite': r'électricité[^\.:]*[:\.]\s*([^\.\n]+)',
            'telephone': r'indicatif[^\.:]*[:\.]\s*([^\.\n]+)',
        }
        
        text = response.css('body').get() or ''
        
        for key, pattern in info_types.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                infos[key] = self.clean_text(match.group(1))
        
        # Extraire depuis des sections structurées
        practical_sections = response.css('.infos-pratiques li, .practical-info li')
        for item in practical_sections:
            text_item = item.css('::text').get()
            if text_item and ':' in text_item:
                key, value = text_item.split(':', 1)
                infos[self.clean_text(key).lower()] = self.clean_text(value)
        
        return infos if infos else None
    
    def extract_que_voir(self, response):
        """Extrait les lieux à voir"""
        que_voir = []
        
        # Sélecteurs pour les attractions
        selectors = [
            '#que-voir li::text',
            '.attractions li::text',
            '.top-sites li::text',
            'section[class*="voir"] li::text',
        ]
        
        for selector in selectors:
            items = response.css(selector).getall()
            if items:
                que_voir.extend([self.clean_text(item) for item in items])
        
        # Chercher les titres h3/h4 dans une section appropriée
        if not que_voir:
            titres = response.css('article h3::text, article h4::text').getall()
            que_voir = [self.clean_text(t) for t in titres[:10]]
        
        return que_voir if que_voir else None
    
    def extract_months_from_text(self, text):
        """Extrait les mois depuis le texte"""
        if not text:
            return []
        
        mois = [
            'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
            'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
        ]
        
        found_months = []
        text_lower = text.lower()
        
        for month in mois:
            if month in text_lower:
                found_months.append(month.capitalize())
        
        return list(set(found_months))  # Supprimer les doublons
    
    def clean_text(self, text):
        """Nettoie le texte extrait"""
        if not text:
            return ""
        
        if isinstance(text, list):
            text = ' '.join(text)
        
        # Enlever les espaces multiples et les retours à la ligne
        text = re.sub(r'\s+', ' ', text)
        # Enlever les espaces en début et fin
        text = text.strip()
        # Enlever les caractères spéciaux problématiques
        text = text.replace('\xa0', ' ')
        
        return text
    
    def handle_error(self, failure):
        """Gestion des erreurs"""
        self.logger.error(f"Erreur de scraping: {failure.value}")
        capitale = failure.request.meta.get('capitale', 'Inconnue')
        self.logger.error(f"Échec pour la capitale: {capitale}")


class AlternativeCapitalsSpider(scrapy.Spider):
    """
    Spider alternatif utilisant la structure d'URL que vous avez fournie
    /fr/guide/europe/pays/ville
    """
    name = 'european_capitals_alt'
    allowed_domains = ['routard.com']
    
    # URLs avec la nouvelle structure
    CAPITALS_URLS = {
        'Dublin': 'https://www.routard.com/fr/guide/europe/irlande/dublin',
        'Paris': 'https://www.routard.com/fr/guide/europe/france/paris',
        'Londres': 'https://www.routard.com/fr/guide/europe/royaume-uni/londres',
        'Berlin': 'https://www.routard.com/fr/guide/europe/allemagne/berlin',
        'Madrid': 'https://www.routard.com/fr/guide/europe/espagne/madrid',
        'Rome': 'https://www.routard.com/fr/guide/europe/italie/rome',
        'Lisbonne': 'https://www.routard.com/fr/guide/europe/portugal/lisbonne',
        'Amsterdam': 'https://www.routard.com/fr/guide/europe/pays-bas/amsterdam',
        'Bruxelles': 'https://www.routard.com/fr/guide/europe/belgique/bruxelles',
        'Vienne': 'https://www.routard.com/fr/guide/europe/autriche/vienne',
        'Prague': 'https://www.routard.com/fr/guide/europe/republique-tcheque/prague',
        'Budapest': 'https://www.routard.com/fr/guide/europe/hongrie/budapest',
        'Varsovie': 'https://www.routard.com/fr/guide/europe/pologne/varsovie',
        'Copenhague': 'https://www.routard.com/fr/guide/europe/danemark/copenhague',
        'Stockholm': 'https://www.routard.com/fr/guide/europe/suede/stockholm',
        'Helsinki': 'https://www.routard.com/fr/guide/europe/finlande/helsinki',
        'Oslo': 'https://www.routard.com/fr/guide/europe/norvege/oslo',
        'Athènes': 'https://www.routard.com/fr/guide/europe/grece/athenes',
        'Bucarest': 'https://www.routard.com/fr/guide/europe/roumanie/bucarest',
        'Sofia': 'https://www.routard.com/fr/guide/europe/bulgarie/sofia',
    }
    
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS': 2,
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    def start_requests(self):
        """Démarre le scraping"""
        for capitale, url in self.CAPITALS_URLS.items():
            yield scrapy.Request(
                url=url,
                callback=EuropeanCapitalsSpider.parse_capitale,
                meta={'capitale': capitale},
                errback=EuropeanCapitalsSpider.handle_error
            )