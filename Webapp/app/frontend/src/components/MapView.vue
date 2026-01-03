<template>
  <div class="map-layout">
    <div class="map-container">
      <l-map ref="map" v-model:zoom="zoom" v-model:center="center" :options="{zoomControl: true}">
        <l-tile-layer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"></l-tile-layer>
        <l-marker
          v-for="city in cities"
          :key="city.capitale" 
          :lat-lng="[city.lat, city.lon]"
          @click="selectCity(city)"
        ></l-marker>
      </l-map>
    </div>

    <transition name="slide">
      <div class="info-panel" v-if="selectedCity">
        <div class="panel-header">
          <button class="close-btn" @click="selectedCity = null">✕</button>
          <h2>{{ selectedCity.capitale_display }}</h2>
        </div>

        <div class="stats-grid">
          <div class="stat-box">🕒 {{ selectedCity.decalage || '0h' }}</div>
          <div class="stat-box">🗓️ {{ selectedCity.quand_partir || 'Toute l\'année' }}</div>
        </div>

        <div class="panel-section">
          <h3>À propos</h3>
          <p class="city-desc">{{ selectedCity.description }}</p>
        </div>
        
        <div class="panel-section">
          <div class="section-title">
            <h3>🍴 Restaurants Michelin</h3>
          </div>

          <div class="filter-group" v-if="availableCuisines.length > 0">
            <button :class="{ active: currentFilter === 'Tous' }" @click="currentFilter = 'Tous'">Tous</button>
            <button 
              v-for="c in availableCuisines" :key="c.raw"
              :class="{ active: currentFilter === c.raw }"
              @click="currentFilter = c.raw"
            >
              {{ c.clean }}
            </button>
          </div>

          <div v-if="loadingRestos" class="loader">Chargement...</div>
          <div v-else class="resto-scroll">
            <div v-for="r in filteredRestaurants" :key="r.nom" class="resto-card">
              <img v-if="r.images && r.images[0]" :src="r.images[0]" class="resto-img" />
              <div class="resto-body">
                <span class="cuisine-tag">{{ cleanName(r.type_cuisine) }}</span>
                <h4>{{ r.nom }}</h4>
                <a :href="r.url" target="_blank">Voir sur Michelin ↗</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import "leaflet/dist/leaflet.css";
import { LMap, LTileLayer, LMarker } from "@vue-leaflet/vue-leaflet";

export default {
  components: { LMap, LTileLayer, LMarker },
  props: ['selectedFromSearch'],
  data() {
    return {
      zoom: 4,
      center: [48.8566, 2.3522],
      cities: [],
      restaurants: [],
      selectedCity: null,
      loadingRestos: false,
      currentFilter: 'Tous'
    };
  },
  computed: {
    availableCuisines() {
      const rawTypes = [...new Set(this.restaurants.map(r => r.type_cuisine).filter(t => t))];
      return rawTypes.map(t => ({
        raw: t,
        clean: this.cleanName(t)
      })).filter(obj => obj.clean.length > 2); // Filtre les petits mots comme "at", "in"
    },
    filteredRestaurants() {
      if (this.currentFilter === 'Tous') return this.restaurants;
      return this.restaurants.filter(r => r.type_cuisine === this.currentFilter);
    }
  },
  watch: {
    selectedFromSearch(newVal) {
      if (newVal) this.selectCity(newVal);
      else this.resetToHome();
    }
  },
  methods: {
    cleanName(text) {
      if (!text) return "";
      // Enlève "Cuisine" et les mots de liaison inutiles
      return text.replace(/cuisine/gi, '').replace(/\b(that|in|at|the|a)\b/gi, '').trim();
    },
    resetToHome() {
      this.selectedCity = null;
      this.zoom = 4;
      this.center = [48.8566, 2.3522];
      this.restaurants = [];
    },
    async fetchCapitals() {
      const res = await fetch("http://localhost:5000/api/capitals");
      this.cities = await res.json();
    },
    async selectCity(city) {
      this.selectedCity = city;
      this.center = [city.lat, city.lon];
      this.zoom = 12;
      this.loadingRestos = true;
      this.currentFilter = 'Tous';
      try {
        const name = city.capitale_display || city.capitale;
        const res = await fetch(`http://localhost:5000/api/restaurants/${encodeURIComponent(name)}`);
        this.restaurants = await res.json();
      } finally { this.loadingRestos = false; }
    }
  },
  mounted() { this.fetchCapitals(); }
};
</script>

<style scoped>
.map-layout { width: 100%; height: 100%; position: relative; }
.map-container { width: 100%; height: 100%; z-index: 1; }

.info-panel {
  position: absolute; right: 0; top: 0; bottom: 0; width: 420px;
  background: white; z-index: 2000; padding: 25px;
  box-shadow: -5px 0 20px rgba(0,0,0,0.15); overflow-y: auto;
}

.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.close-btn { border: none; background: #f1f5f9; width: 30px; height: 30px; border-radius: 50%; cursor: pointer; }

.stats-grid { display: flex; gap: 10px; margin-bottom: 20px; }
.stat-box { flex: 1; background: #f8fafc; padding: 10px; border-radius: 8px; font-size: 0.85rem; font-weight: 600; text-align: center; }

.city-desc { font-size: 0.95rem; line-height: 1.6; color: #475569; }

.filter-group { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 20px; }
.filter-group button { 
  padding: 5px 12px; border-radius: 20px; border: 1px solid #e2e8f0; 
  background: white; font-size: 0.75rem; cursor: pointer;
}
.filter-group button.active { background: #3b82f6; color: white; border-color: #3b82f6; }

.resto-card { border: 1px solid #e2e8f0; border-radius: 12px; margin-bottom: 20px; overflow: hidden; }
.resto-img { width: 100%; height: 140px; object-fit: cover; }
.resto-body { padding: 15px; }
.cuisine-tag { font-size: 10px; background: #dcfce7; color: #166534; padding: 3px 8px; border-radius: 4px; text-transform: capitalize; font-weight: 700; }
.resto-body h4 { margin: 8px 0; }
.resto-body a { color: #ea580c; text-decoration: none; font-size: 0.85rem; font-weight: 700; }

.slide-enter-active, .slide-leave-active { transition: transform 0.3s ease; }
.slide-enter-from, .slide-leave-to { transform: translateX(100%); }
</style>