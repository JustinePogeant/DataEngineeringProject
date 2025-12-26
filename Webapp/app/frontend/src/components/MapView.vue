<template>
  <div class="app-layout">
    <div id="map"></div>
    
    <div v-if="searchQuery" class="search-feedback-container">
      <ul v-if="searchResults.length === 0" class="global-search-results">
        <li class="no-result">Informations indisponibles</li>
      </ul>
      
      <ul v-else class="global-search-results">
        <li v-for="city in searchResults" :key="city.capitale" @click="selectCity(city)">
          {{ city.capitale }}
        </li>
      </ul>
    </div>

    <div v-if="selectedCity" class="sidebar">
      <button @click="selectedCity = null" class="close-btn">×</button>
      <h2>📍 {{ selectedCity.capitale }}</h2>
      <p class="meta">🕒 {{ selectedCity.decalage }} | 📅 {{ selectedCity.quand_partir || 'Toute l\'année' }}</p>
      <hr>
      
      <div class="description-section">
        <h3>📖 À propos</h3>
        <p class="desc">{{ selectedCity.description }}</p>
      </div>
      
      <div class="restaurants-section">
        <h3>🍴 Restaurants Michelin</h3>
        <div v-if="restaurants.length === 0" class="empty">Aucun restaurant trouvé pour cette ville.</div>
        <div v-for="r in restaurants" :key="r.nom" class="resto-card">
          <strong>{{ r.nom }}</strong>
          <p>{{ r.type_cuisine }} • <span class="price">{{ r.prix_niveau }}</span></p>
          <small v-if="r.adresse">📍 {{ r.adresse }}</small>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// SVG personnalisé pour les marqueurs (évite les erreurs 404 et blocages navigateurs)
const iconSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#e74c3c" width="32px" height="32px"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-9-7-9zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>`;
const customIcon = L.divIcon({ html: iconSvg, className: '', iconSize: [32, 32], iconAnchor: [16, 32] });

// Dictionnaire de coordonnées pour placer les points sur la carte
const cityCoords = {
  "Dublin": [53.3498, -6.2603], "Berlin": [52.5200, 13.4050], "Lisbonne": [38.7223, -9.1393],
  "Rome": [41.8902, 12.4922], "Madrid": [40.4168, -3.7038], "Bruxelles": [50.8503, 4.3517],
  "Vienne": [48.2082, 16.3738], "Stockholm": [59.3293, 18.0686], "Copenhague": [55.6761, 12.5683],
  "Budapest": [47.4979, 19.0402], "Athènes": [37.9838, 23.7275], "Ljubljana": [46.0569, 14.5058],
  "Tallinn": [59.4370, 24.7536], "Vilnius": [54.6872, 25.2797], "Nicosie": [35.1856, 33.3823]
};

export default {
  props: ['searchQuery'],
  data() {
    return {
      map: null,
      selectedCity: null,
      restaurants: [],
      allCities: [],
      searchResults: []
    };
  },
  watch: {
    // Surveille la barre de recherche (reçue depuis App.vue)
    searchQuery(newVal) {
      if (!newVal) {
        this.searchResults = [];
        return;
      }
      this.searchResults = this.allCities.filter(c => 
        c.capitale.toLowerCase().includes(newVal.toLowerCase())
      ).slice(0, 5);
    },
    // Charge les restaurants quand une ville est sélectionnée
    async selectedCity(newCity) {
      if (newCity) {
        this.restaurants = [];
        const name = this.cleanName(newCity.capitale);
        try {
          const res = await fetch(`http://localhost:5000/api/restaurants/${name}`);
          this.restaurants = await res.json();
        } catch (e) {
          console.error("Erreur restaurants:", e);
        }
      }
    }
  },
  methods: {
    cleanName(n) {
      if (n.includes('Lisbonne')) return 'Lisbonne';
      if (n.includes('Bruxelles')) return 'Bruxelles';
      if (n.includes('Vienne')) return 'Vienne';
      if (n.includes('Budapest')) return 'Budapest';
      return n.split(' ').pop();
    },
    selectCity(city) {
      this.selectedCity = city;
      this.searchResults = [];
      this.$emit('city-selected'); // Informe App.vue de vider l'input
      
      const name = this.cleanName(city.capitale);
      const coords = cityCoords[name] || cityCoords[city.capitale] || [48.85, 12.0];
      this.map.flyTo(coords, 8);
    }
  },
  async mounted() {
    // Initialisation carte
    this.map = L.map('map').setView([48.85, 12.0], 4);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap'
    }).addTo(this.map);

    // Récupération des données
    try {
      const res = await fetch('http://localhost:5000/api/capitals');
      this.allCities = await res.json();
      
      this.allCities.forEach(city => {
        const name = this.cleanName(city.capitale);
        const coords = cityCoords[name] || cityCoords[city.capitale];
        
        if (coords) {
          L.marker(coords, { icon: customIcon }).addTo(this.map).on('click', () => {
            this.selectedCity = city;
          });
        }
      });
    } catch (e) {
      console.error("Erreur API Capitals:", e);
    }
  }
}
</script>

<style scoped>
.app-layout { display: flex; flex: 1; position: relative; height: 100%; }
#map { flex: 1; z-index: 1; }

/* Résultats de recherche flottants */
.search-feedback-container {
  position: absolute; top: 0px; right: 30px; width: 300px; z-index: 3000;
}
.global-search-results {
  background: white; list-style: none; padding: 0; margin: 0;
  border-radius: 0 0 12px 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}
.global-search-results li {
  padding: 12px 20px; cursor: pointer; border-bottom: 1px solid #eee;
}
.global-search-results li:hover { background: #f8f9fa; }
.no-result { color: #999; font-style: italic; cursor: default !important; background: #fff !important; }

/* Sidebar */
.sidebar {
  position: absolute; right: 20px; top: 20px; bottom: 20px; width: 380px;
  background: white; z-index: 1000; padding: 25px; border-radius: 12px;
  box-shadow: 0 4px 25px rgba(0,0,0,0.3); overflow-y: auto;
}
.close-btn {
  float: right; cursor: pointer; border: none; background: #f0f0f0; 
  border-radius: 50%; width: 30px; height: 30px; font-weight: bold;
}
.meta { color: #666; font-size: 0.9em; margin-bottom: 15px; }
.desc { line-height: 1.6; color: #444; font-size: 0.95em; }

/* Restaurants */
.resto-card {
  background: #f8f9fa; padding: 12px; margin-bottom: 10px; 
  border-left: 4px solid #e74c3c; border-radius: 4px;
}
.price { color: #27ae60; font-weight: bold; }
h3 { border-bottom: 2px solid #eee; padding-bottom: 5px; color: #2c3e50; }
</style>