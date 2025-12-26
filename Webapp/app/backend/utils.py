import re
import html

def get_city_coordinates(city_name):
    """Retourne les coordonnées [lat, lon] pour la carte Leaflet"""
    coords = {
        "Dublin": [53.3498, -6.2603],
        "Berlin": [52.5200, 13.4050],
        "Lisbonne": [38.7223, -9.1393],
        "Rome": [41.9028, 12.4964],
        "Madrid": [40.4168, -3.7038],
        "Bruxelles": [50.8503, 4.3517],
        "Vienne": [48.2082, 16.3738],
        "Stockholm": [59.3293, 18.0686],
        "Copenhague": [55.6761, 12.5683],
        "Budapest": [47.4979, 19.0402],
        "Athènes": [37.9838, 23.7275],
        "Ljubljana": [46.0569, 14.5058],
        "Tallinn": [59.4370, 24.7535],
        "Vilnius": [54.6872, 25.2797],
        "Nicosie": [35.1856, 33.3823]
    }
    return coords.get(city_name, [48.8566, 2.3522]) # Par défaut Paris si non trouvé