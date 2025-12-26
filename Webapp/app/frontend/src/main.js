import { createApp } from 'vue'
import App from './App.vue'

// Importation globale des styles si nécessaire
// (Note : le CSS de Leaflet est déjà importé dans MapView.vue, 
// mais on peut aussi le mettre ici pour qu'il soit disponible partout)

const app = createApp(App)

// Montage de l'application sur la div avec l'id "app" (définie dans index.html)
app.mount('#app')