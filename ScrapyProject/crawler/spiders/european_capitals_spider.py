import scrapy
from datetime import datetime
import re


class EuropeanCapitalsSpider(scrapy.Spider):
    """
    Spider pour scraper les informations des capitales européennes
    sur le Guide du Routard avec la nouvelle structure de page.
    """
    name = 'european_capitals1'
    allowed_domains = ['routard.com']

    # Liste des capitales européennes avec leurs URLs
    EUROPEAN_CAPITALS = {
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
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
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
                meta={'capitale': capitale},
                errback=self.handle_error,
                dont_filter=True
            )

    def parse_capitale(self, response):
        """Parse la page d'une capitale"""
        capitale = response.meta['capitale']

        if response.status in [403, 404]:
            self.logger.warning(f"Erreur {response.status} pour {capitale}: {response.url}")
            return

        self.logger.info(f"Parsing {capitale}: {response.url}")

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

    # --- Méthodes d'extraction ---

    def extract_pays(self, response):
        """Extrait le nom du pays"""
        pays = response.css('.breadcrumb a::text').getall()
        if len(pays) >= 2:
            return self.clean_text(pays[-2])
        titre = response.css('h1::text').get()
        if titre and ',' in titre:
            return self.clean_text(titre.split(',')[-1])
        return "Non spécifié"

    def extract_description(self, response):
        """Extrait la description principale"""
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
        all_paragraphs = response.css('p::text').getall()
        if all_paragraphs:
            return self.clean_text(' '.join(all_paragraphs[:3]))
        return "Description non disponible"

    def extract_a_propos(self, response):
        """Extrait la section 'À propos'"""
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
        temp_data = {}
        rows = response.css('table.meteo tr, table.climat tr, .weather-table tr')
        for row in rows:
            mois = row.css('th::text, td:first-child::text').get()
            temp = row.css('td::text').getall()
            if mois and temp:
                temp_data[self.clean_text(mois)] = [self.clean_text(t) for t in temp]
        return temp_data if temp_data else None

    def extract_carte(self, response):
        """Extrait l'URL de la carte"""
        carte_url = response.xpath('//*[@id="rtd-guide-pa-nav"]/ul/li[1]/a/@data-modified-href').get()
        if carte_url:
            return response.urljoin(carte_url)
        return None

    def extract_infos_pratiques(self, response):
        """Extrait les informations pratiques"""
        infos = {}
        infos_pratiques_text = response.xpath('//*[@id="rtd-guide-pa-nav"]/ul/li[9]/a/div/span/text()').get()
        if infos_pratiques_text:
            infos['infos_pratiques'] = infos_pratiques_text.strip()
        return infos if infos else None

    def extract_que_voir(self, response):
        """Extrait les lieux à voir"""
        que_voir = []
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
        return list(set(found_months))

    def clean_text(self, text):
        """Nettoie le texte extrait"""
        if not text:
            return ""
        if isinstance(text, list):
            text = ' '.join(text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        text = text.replace('\xa0', ' ')
        return text

    def handle_error(self, failure):
        """Gestion des erreurs"""
        self.logger.error(f"Erreur de scraping: {failure.value}")
        capitale = failure.request.meta.get('capitale', 'Inconnue')
        self.logger.error(f"Échec pour la capitale: {capitale}")
