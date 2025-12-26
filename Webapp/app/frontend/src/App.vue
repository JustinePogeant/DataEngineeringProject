<template>
  <div id="app">
    <header class="navbar">
      <h1>🌍 Guide Europe</h1>
      <div class="search-container">
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Rechercher une ville..."
        >
      </div>
    </header>

    <main>
      <MapView :search-query="searchQuery" @city-selected="clearSearch" />
    </main>

    <footer class="footer">
      <div class="footer-content">
        <span class="author">Par : <strong>Ouchaou Lina et Pogeant Justine</strong></span>
        <span class="school">École : <strong>ESIEE Paris</strong></span>
        <span class="date"> Date de création : <strong>Décembre 2025</strong></span>
      </div>
    </footer>
  </div>
</template>

<script>
import MapView from './components/MapView.vue'

export default {
  name: 'App',
  components: { MapView },
  data() {
    return { searchQuery: '' }
  },
  methods: {
    clearSearch() {
      this.searchQuery = '';
    }
  }
}
</script>

<style>
/* Style global */
body { margin: 0; font-family: 'Segoe UI', Tahoma, sans-serif; overflow: hidden; }

#app { 
  height: 100vh; 
  display: flex; 
  flex-direction: column; 
}

/* Navbar */
.navbar { 
  background: #2c3e50; 
  color: white; 
  padding: 0 30px; 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  height: 60px; 
  box-shadow: 0 2px 10px rgba(0,0,0,0.2);
  z-index: 2000;
}

.search-container input {
  padding: 8px 20px; 
  border-radius: 20px; 
  border: none; 
  width: 250px;
  outline: none;
}

/* Zone principale */
main { 
  flex: 1; 
  position: relative; 
  overflow: hidden; 
}

/* Nouveau Footer */
.footer {
  background: #f8f9fa;
  color: #555;
  border-top: 1px solid #ddd;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  z-index: 2000;
}

.footer-content {
  display: flex;
  gap: 30px; /* Espace entre les infos */
}

.footer-content strong {
  color: #2c3e50;
}
</style>