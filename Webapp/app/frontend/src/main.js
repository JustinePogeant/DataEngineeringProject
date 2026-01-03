import { createApp } from 'vue'
import App from './App.vue'

// Importation de Leaflet CSS globalement pour que la carte s'affiche bien
import 'leaflet/dist/leaflet.css';

const app = createApp(App);
app.mount('#app');