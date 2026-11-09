import sys
import json
import pathlib
import random
import shutil
import os
import requests

EUROPEANA_KEY = os.environ.get("EUROPEANA_API_KEY")

# Dictionnaire de traduction (Espagnol -> Anglais) pour matcher les noms de fichiers
TRANSLATIONS = {
    "espada": "sword", "rey": "king", "reina": "queen",
    "batalla": "battle", "castillo": "castle", "iglesia": "church",
    "barco": "ship", "muerte": "death", "oro": "gold", "libro": "book",
    "pintura": "painting", "retrato": "portrait", "soldado": "soldier",
    "guerra": "war", "corona": "crown", "inquisicion": "inquisition",
    "teatro": "theater", "palacio": "palace", "biblioteca": "library",
    "mosaico": "mosaic", "olimpiadas": "olympic", "caballo": "horse",
    "flor": "flower", "arbol": "tree", "agua": "water",
    "arquitectura": "architecture", "escultura": "sculpture",
    "puente": "bridge", "torre": "tower", "muralla": "wall",
    "escudo": "shield", "bandera": "flag", "reloj": "clock",
    "trafalgar": "trafalgar", "goya": "goya", "alhambra": "alhambra",
    "segovia": "segovia", "acueducto": "aqueduct", "catedral": "cathedral",
    "giralda": "giralda", "sevilla": "sevilla", "salamanca": "salamanca",
    "granada": "granada", "madrid": "madrid", "toledo": "toledo"
}

def search_by_filename(text_to_search):
    """Cherche une image dont le nom contient un mot-clé du texte."""
    assets_dir = pathlib.Path("assets/history")
    if not assets_dir.exists():
        return None
    
    search_terms = []
    for es_word, en_word in TRANSLATIONS.items():
        if es_word in text_to_search:
            search_terms.append(en_word)
    
    if not search_terms:
        return None
    
    matching_images = []
    for img in assets_dir.glob("*.jpg"):
        img_name_lower = img.name.lower()
        for term in search_terms:
            if term in img_name_lower:
                matching_images.append(img)
                break
    
    if matching_images:
        return random.choice(matching_images)
    return None

def search_europeana(query):
    """Cherche une image libre de droits sur Europeana."""
    if not EUROPEANA_KEY:
        print("⚠️ Pas de clé EUROPEANA_API_KEY.")
        return None
    url = "https://api.europeana.eu/record/v2/search.json"
    params = {
        "wskey": EUROPEANA_KEY,
        "query": query,
        "reusability": "open",
        "media": "true",
        "qf": "TYPE:IMAGE",
        "rows": 5
    }
    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        items = data.get("items", [])
        for item in items:
            image_url = item.get("edmIsShownBy", [None])[0]
            if image_url:
                title = item.get("title", ["Sans titre"])[0]
                print(f"✅ Image Europeana : {title[:50]}...")
                return image_url
    except Exception as e:
        print(f"❌ Erreur Europeana : {e}")
    return None

def get_best_image(narration, hook, media_prompt=""):
    text_to_search = (narration + " " + hook).lower()
    media_dir = pathlib.Path("media")
    media_dir.mkdir(exist_ok=True)
    final_path = media_dir / "image_01.jpg"
    
    # NIVEAU 1 : Sujets manuels (sujets.json)
    if pathlib.Path("sujets.json").exists():
        sujets = json.loads(pathlib.Path("sujets.json").read_text(encoding="utf-8"))
        for keyword, image_path in sujets.items():
            if keyword in text_to_search and pathlib.Path(image_path).exists():
                print(f"✅ [Manuel] {keyword} -> {image_path}")
                shutil.copy(image_path, final_path)
                return final_path
    
    # NIVEAU 1.5 : Recherche par nom de fichier (Google Flow)
    img = search_by_filename(text_to_search)
    if img:
        print(f"✅ [Nom de fichier] {img.name}")
        shutil.copy(img, final_path)
        return final_path
    
    # NIVEAU 2 : Recherche Europeana
    query = media_prompt if media_prompt else hook.split(":")[0].strip()
    if len(query) > 80:
        query = query[:80]
    image_url = search_europeana(query)
    if image_url:
        try:
            img_data = requests.get(image_url, timeout=60).content
            final_path.write_bytes(img_data)
            print("✅ Image Europeana téléchargée.")
            return final_path
        except Exception as e:
            print(f"❌ Erreur téléchargement : {e}")
    
    # NIVEAU 3 : Hasard
    images = list(pathlib.Path("assets/history").glob("*.jpg"))
    if images:
        selected = random.choice(images)
        print(f"⚠️ [Hasard] {selected.name}")
        shutil.copy(selected, final_path)
        return final_path
    
    return None

if __name__ == "__main__":
    json_file = sys.argv[1]
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    narration = data.get("narration", "")
    hook = data.get("hook", "")
    media_prompt = data.get("media_prompt", "")
    
    image_path = get_best_image(narration, hook, media_prompt)
    
    if image_path:
        data["media"] = [{"path": str(image_path)}]
        pathlib.Path(json_file).write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print("✅ JSON mis à jour.")
    else:
        print("❌ Impossible de trouver une image.")
        sys.exit(1)
