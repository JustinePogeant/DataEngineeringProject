BOT_NAME = "crawler"

SPIDER_MODULES = ["crawler.spiders"]
NEWSPIDER_MODULE = ["crawler.spiders"]

# Respecter robots.txt
ROBOTSTXT_OBEY = False

# Assurez-vous que ceci n'est PAS à False
COMPRESSION_ENABLED = True

# User-Agent réaliste
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Délais et concurrence
CONCURRENT_REQUESTS = 4
DOWNLOAD_DELAY = 3
CONCURRENT_REQUESTS_PER_DOMAIN = 2
CONCURRENT_REQUESTS_PER_IP = 2

# Cookies
COOKIES_ENABLED = True

# Telnet Console (désactivé)
TELNETCONSOLE_ENABLED = False

# Headers par défaut - CRUCIAL POUR ÉVITER LE CONTENU COMPRESSÉ
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Extensions
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
    'scrapy.extensions.logstats.LogStats': 500,
}

# Pipelines - ACTIVÉS
ITEM_PIPELINES = {
    'crawler.pipelines.RoutardPipeline': 300,
}

# Downloader Middlewares - IMPORTANT POUR LA DÉCOMPRESSION
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
}

# Retry settings
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]

# AutoThrottle
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 3
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
AUTOTHROTTLE_DEBUG = False

# HTTP Cache
HTTPCACHE_ENABLED = False
HTTPCACHE_EXPIRATION_SECS = 86400
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [500, 502, 503, 504]
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


FEED_EXPORT_ENCODING = 'utf-8'

# Logging
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'

# Feed exports - ENCODAGE UTF-8
FEEDS = {
    'capitals_%(time)s.json': {
        'format': 'json',
        'encoding': 'utf-8',
        'ensure_ascii': False,
        'indent': 2,
        'store_empty': False,
    },
}

# Profondeur maximale
DEPTH_LIMIT = 2

# Timeout
DOWNLOAD_TIMEOUT = 30

# Redirect
REDIRECT_ENABLED = True
REDIRECT_MAX_TIMES = 3

# Encodage par défaut
FEED_EXPORT_ENCODING = 'utf-8'