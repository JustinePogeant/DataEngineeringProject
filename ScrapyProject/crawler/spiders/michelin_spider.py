import scrapy
from datetime import datetime
import re

class MichelinSpider(scrapy.Spider):
    """Spider pour scraper les restaurants du Guide Michelin"""

    name = "michelin_spider"
    allowed_domains = ["guide.michelin.com"]

    # URLs des capitales européennes
    start_urls = [
        "https://guide.michelin.com/fr/fr/ile-de-france/paris/restaurants",
        "https://guide.michelin.com/fr/fr/comunidad-de-madrid/madrid/restaurants",
        "https://guide.michelin.com/fr/fr/lazio/roma/restaurants",
        "https://guide.michelin.com/fr/fr/lisboa-region/lisboa/restaurants",
        "https://guide.michelin.com/fr/fr/berlin-region/berlin/restaurants",
        "https://guide.michelin.com/fr/fr/noord-holland/amsterdam/restaurants",
        "https://guide.michelin.com/fr/fr/vienna/restaurants",
        "https://guide.michelin.com/fr/fr/bruxelles-capitale/bruxelles/restaurants",
        "https://guide.michelin.com/fr/fr/prague/restaurants",
        "https://guide.michelin.com/fr/fr/dublin/dublin/restaurants",
    ]

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'FEEDS': {
            'michelin_restaurants.json': {
                'format': 'json',
                'encoding': 'utf-8',
                'indent': 4,
                'overwrite': True
            }
        }
    }

    def parse(self, response):
        """Parse la page de listing des restaurants"""

        capitale = self.get_capitale_from_url(response.url)
        self.logger.info(f"📍 Scraping des restaurants à {capitale}")

        # Sélectionner tous les restaurants
        restaurants = response.css('div.card__menu')
        self.logger.info(f"📍 Trouvé {len(restaurants)} restaurants à {capitale}")

        if not restaurants:
            self.logger.warning(f"⚠️ Aucun restaurant trouvé pour {capitale}")
            return

        restaurants_data = []

        for resto in restaurants:
            # Nom du restaurant
            nom = resto.css('h3.card__menu-content--title a::text').get()
            if not nom:
                nom = resto.css('h3.card__menu-content--title::text').get()

            # URL de la page détaillée
            url = resto.css('h3.card__menu-content--title a::attr(href)').get()
            if url:
                url = response.urljoin(url)

            # Prix (symboles €)
            prix_text = resto.css('div.card__menu-footer--price::text').get()
            prix_niveau = self.extract_price_level(prix_text)

            restaurants_data.append({
                'nom': self.clean_text(nom),
                'capitale': capitale,
                'prix': self.clean_text(prix_text),
                'prix_niveau': prix_niveau,
                'url': url
            })

        # Trier par prix (du moins cher au plus cher)
        restaurants_data.sort(key=lambda x: x['prix_niveau'])
        self.logger.info(f"💰 {len(restaurants_data)} restaurants après tri par prix")

        # Prendre les 10 restaurants les moins chers
        top_10 = restaurants_data[:10]

        # Scraper les détails de chaque restaurant
        for resto in top_10:
            if resto['url']:
                yield scrapy.Request(
                    url=resto['url'],
                    callback=self.parse_detail,
                    meta={'resto_base': resto}
                )

    def parse_detail(self, response):
        """Parse la page détaillée d'un restaurant"""

        resto_base = response.meta['resto_base']
        nom = resto_base['nom']

        self.logger.info(f"🔍 Scraping détails: {nom}")

        # ========== NOM ==========
        nom_detail = response.css('h1.data-sheet__title::text').get()
        if nom_detail:
            nom = self.clean_text(nom_detail)

        # ========== ADRESSE COMPLÈTE (D'ABORD !) ==========
        adresse = None

        # Sélecteur principal
        adresse_raw = response.css('div.data-sheet__block--text::text').get()

        if adresse_raw:
            adresse = ' '.join(adresse_raw.split()).strip()
        else:
            # Fallback
            adresse_parts = response.css('ul.restaurant-details__heading--list li::text').getall()
            if adresse_parts:
                adresse = ', '.join([part.strip() for part in adresse_parts if part.strip()])

        # ========== VILLE (APRÈS adresse) ==========
        """ville = None
        
        # Extraire la ville depuis l'adresse
        if adresse and ',' in adresse:
            parts = [p.strip() for p in adresse.split(',')]
            if len(parts) >= 2:
                # Prendre l'avant-dernière partie (souvent la ville)
                ville = parts[-2]
        
        # Fallback : chercher dans le span city
        if not ville:
            ville = response.css('span.data-sheet__city::text').get()"""

        # ========== TYPE DE CUISINE ==========
        type_cuisine = None

        # Méthode 1 : Tags/labels
        cuisine_labels = response.css('div.data-sheet__classification--list span::text').getall()
        if cuisine_labels:
            type_cuisine = ', '.join([self.clean_text(c) for c in cuisine_labels if c.strip()])

        # Méthode 2 : Bloc spécifique
        if not type_cuisine:
            type_cuisine = response.css('div.restaurant-details__classification-item::text').get()

        # Méthode 3 : Regex dans la description
        if not type_cuisine:
            description_preview = response.css('div.data-sheet__description::text').get()
            if description_preview:
                match = re.search(r'(Cuisine\s+\w+|cuisine\s+\w+)', description_preview)
                if match:
                    type_cuisine = match.group(1)

        # ========== DESCRIPTION COMPLÈTE ==========
        description = None

        # Méthode 1 : Bloc principal
        description_parts = response.css('div.data-sheet__description::text, div.data-sheet__description p::text').getall()
        if description_parts:
            description = ' '.join([self.clean_text(p) for p in description_parts if p.strip()])

        # Méthode 2 : Alternative
        if not description:
            description = response.css('div.restaurant-details__description p::text').get()

        # Méthode 3 : Meta description
        if not description:
            description = response.css('meta[name="description"]::attr(content)').get()

        # ========== TÉLÉPHONE ==========
        telephone = response.css('a[href^="tel:"]::text').get()
        if not telephone:
            telephone = response.css('div.data-sheet__block--text a[data-dtm*="phone"]::text').get()

        # ========== SITE WEB ==========
        site_web = response.css('a.data-sheet__block--text[href^="http"]::attr(href)').get()
        if not site_web:
            site_web = response.css('a[data-event*="CTA_website"]::attr(href)').get()

        # ========== IMAGES ==========
        images = []

        # Images du carousel
        carousel_images = response.css('div.gallery-mosaic__carousel img::attr(data-src)').getall()
        if not carousel_images:
            carousel_images = response.css('div.gallery-mosaic__carousel img::attr(src)').getall()
        images.extend(carousel_images)

        # Images de la galerie
        gallery_attr = response.css('div.icon-box img::attr(data-gallery-image)').get()
        if gallery_attr:
            gallery_images = [img.strip() for img in gallery_attr.split(',')]
            images.extend(gallery_images)

        # Images lazy loading
        lazy_images = response.css('img[ci-bg-url]::attr(ci-bg-url)').getall()
        images.extend(lazy_images)

        # Fallback
        if not images:
            images = response.css('img.restaurant-details__image::attr(src)').getall()

        # Nettoyage et limitation
        images = list(dict.fromkeys([img for img in images if img and img.strip()]))[:5]

        # ========== LOG DES RÉSULTATS ==========
        self.logger.info(f"✅ Scraped: {nom} - {resto_base['prix']}")
        if not type_cuisine:
            self.logger.warning(f"⚠️ Type de cuisine manquant pour {nom}")
        if not description:
            self.logger.warning(f"⚠️ Description manquante pour {nom}")
        if not adresse:
            self.logger.warning(f"⚠️ Adresse manquante pour {nom}")

        # ========== CONSTRUCTION DU RÉSULTAT ==========
        restaurant_data = {
            'nom': nom,
            'capitale': resto_base['capitale'],
            #'ville': self.clean_text(ville) if ville else None,
            'adresse': self.clean_text(adresse) if adresse else None,
            'type_cuisine': self.clean_text(type_cuisine) if type_cuisine else None,
            'description': self.clean_text(description) if description else None,
            #'prix': resto_base['prix'],
            'prix_niveau': resto_base['prix_niveau'],
            'telephone': self.clean_text(telephone) if telephone else None,
            'site_web': site_web,
            'images': images if images else [],
            'url': response.url,
            'date_scraping': datetime.now().isoformat()
        }

        yield restaurant_data

    def get_capitale_from_url(self, url):
        """Détermine la capitale depuis l'URL"""
        mapping = {
            'paris': 'Paris',
            'madrid': 'Madrid',
            'roma': 'Rome',
            'lisboa': 'Lisbonne',
            'berlin': 'Berlin',
            'amsterdam': 'Amsterdam',
            'vienna': 'Vienne',
            'bruxelles': 'Bruxelles',
            'prague': 'Prague',
            'dublin': 'Dublin',
        }

        url_lower = url.lower()
        for key, value in mapping.items():
            if key in url_lower:
                return value
        return "Inconnue"

    def extract_price_level(self, price_text):
        """Extrait le niveau de prix (nombre de €)"""
        if not price_text:
            return 999
        return price_text.count('€')

    def clean_text(self, text):
        """Nettoie le texte"""
        if not text:
            return None
        return ' '.join(text.split()).strip()
