<template>
  <div id="app">
    <header class="navbar">
      <div class="logo-wrapper" @click="resetMap">
        <div class="logo-container">
          <span class="logo-emoji">🌍</span>
          <h1 class="logo-text">Guide Europe</h1>
        </div>
      </div>

      <div class="search-wrapper">
        <div class="search-container">
          <input 
            v-model="searchQuery" 
            @input="onSearch"
            @keyup.enter="handleEnter"
            @focus="showSuggestions = true"
            type="text" 
            placeholder="Rechercher une capitale..."
            autocomplete="off"
          >
          <transition name="fade">
            <ul v-if="showSuggestions && searchQuery.length >= 2" class="suggestions">
              <li v-if="searchResults.length === 0" class="no-result">❌ Ville non trouvée</li>
              <li v-for="res in searchResults" :key="res.capitale" @click="selectResult(res)">
                {{ res.capitale_display || res.capitale }}
              </li>
            </ul>
          </transition>
        </div>
      </div>
    </header>

    <main class="main-content">
      <MapView 
        :selected-from-search="selectedCity" 
        @city-selected="onCitySelectedOnMap" 
      />
    </main>

    <footer class="project-footer">
      <div class="footer-left">🎓 <strong>ESIEE Paris</strong> | Janvier 2026</div>
      <div class="footer-right">Par : <strong>Ouchaou Lina et Pogeant Justine</strong></div>
    </footer>
  </div>
</template>

<script>
import MapView from './components/MapView.vue'

export default {
  name: 'App',
  components: { MapView },
  data() {
    return { 
      searchQuery: '',
      searchResults: [],
      selectedCity: null,
      showSuggestions: false
    }
  },
  methods: {
    resetMap() {
      console.log("App: Reset demandé");
      // On passe par une petite astuce pour forcer le changement même si c'est déjà null
      this.selectedCity = undefined;
      this.$nextTick(() => {
        this.selectedCity = null;
        this.searchQuery = '';
      });
    },
    async onSearch() {
      if (this.searchQuery.length < 2) return;
      try {
        const response = await fetch(`http://localhost:5000/api/search?q=${encodeURIComponent(this.searchQuery)}`);
        this.searchResults = await response.json();
      } catch (error) { console.error("Erreur Search:", error); }
    },
    selectResult(city) {
      this.selectedCity = Object.assign({}, city);
      this.searchQuery = city.capitale_display || city.capitale;
      this.showSuggestions = false;
    },
    handleEnter() {
      if (this.searchResults.length > 0) this.selectResult(this.searchResults[0]);
    },
    onCitySelectedOnMap() { this.showSuggestions = false; }
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body { height: 100%; margin: 0; padding: 0; }
body { font-family: 'Inter', sans-serif; background-color: #f8fafc; overflow: hidden; }

#app { display: flex; flex-direction: column; height: 100vh; width: 100vw; }

.navbar { 
  background: #1e293b; height: 70px; padding: 0 30px; 
  display: flex; align-items: center; justify-content: space-between; 
  z-index: 5000; color: white; flex-shrink: 0;
}

.logo-wrapper { cursor: pointer; padding: 10px; }
.logo-container { display: flex; align-items: center; pointer-events: none; }
.logo-emoji { font-size: 24px; margin-right: 10px; }
.logo-text { font-size: 20px; font-weight: 700; margin: 0; }

.search-wrapper { position: relative; }
.search-container input {
  padding: 10px 20px; width: 300px; border-radius: 20px; border: none;
  background: #334155; color: white; outline: none;
}
.search-container input:focus { background: white; color: #1e293b; }

.suggestions {
  position: absolute; top: 50px; right: 0; background: white; 
  color: #1e293b; width: 100%; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  list-style: none; padding: 5px 0;
}
.suggestions li { padding: 10px 20px; cursor: pointer; border-bottom: 1px solid #eee; }

.main-content { flex: 1; position: relative; width: 100%; overflow: hidden; }

.project-footer {
  background: #0f172a; color: #94a3b8; height: 40px;
  display: flex; justify-content: space-between; align-items: center;
  padding: 0 30px; font-size: 0.8rem; flex-shrink: 0;
}
</style>