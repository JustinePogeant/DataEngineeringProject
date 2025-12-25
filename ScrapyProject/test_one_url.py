"""
Script simple pour tester UNE URL et voir le contenu retourné
"""
import requests
from bs4 import BeautifulSoup

# URL à tester
URL = "https://www.routard.com/guide/europe/irlande/dublin.htm"

# Headers pour simuler un navigateur
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

print("=" * 80)
print(f"🧪 TEST DE L'URL : {URL}")
print("=" * 80)

try:
    # Faire la requête
    print("\n📡 Envoi de la requête...")
    response = requests.get(URL, headers=HEADERS, timeout=10)
    
    print(f"✅ Status Code: {response.status_code}")
    print(f"📊 Content-Length: {len(response.content)} bytes")
    print(f"🔤 Encoding: {response.encoding}")
    print(f"📄 Content-Type: {response.headers.get('Content-Type')}")
    
    # Vérifier si le contenu est lisible
    print("\n" + "=" * 80)
    print("📝 APERÇU DU CONTENU (premiers 500 caractères):")
    print("=" * 80)
    
    # Essayer de décoder le texte
    text = response.text[:500]
    print(text)
    
    # Vérifier si c'est du HTML valide
    print("\n" + "=" * 80)
    print("🔍 ANALYSE HTML:")
    print("=" * 80)
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extraire quelques éléments
    title = soup.find('title')
    print(f"📌 Title: {title.text if title else 'Non trouvé'}")
    
    h1 = soup.find('h1')
    print(f"📌 H1: {h1.text if h1 else 'Non trouvé'}")
    
    # Compter les paragraphes
    paragraphs = soup.find_all('p')
    print(f"📌 Nombre de paragraphes: {len(paragraphs)}")
    
    if paragraphs:
        print(f"\n📄 Premier paragraphe:")
        print(paragraphs[0].get_text()[:200])
    
    # Vérifier le breadcrumb
    breadcrumb = soup.find(class_='breadcrumb')
    if breadcrumb:
        print(f"\n🍞 Breadcrumb trouvé:")
        print(breadcrumb.get_text())
    
    print("\n" + "=" * 80)
    print("✅ TEST TERMINÉ AVEC SUCCÈS")
    print("=" * 80)
    
except requests.exceptions.RequestException as e:
    print(f"\n❌ ERREUR: {e}")
except Exception as e:
    print(f"\n❌ ERREUR INATTENDUE: {e}")

print("\n💡 Conseils:")
print("   - Si vous voyez du texte lisible, l'URL fonctionne !")
print("   - Si vous voyez des caractères bizarres, il y a un problème d'encodage")
print("   - Notez les sélecteurs CSS qui fonctionnent (h1, .breadcrumb, etc.)")