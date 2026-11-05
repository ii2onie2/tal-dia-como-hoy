import sys
import json
import urllib.request
import urllib.parse
import pathlib
import random
import shutil

# URL de secours absolue (fresque de Taüll)
FALLBACK_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Frescos_from_Sant_Climent_de_Ta%C3%BCll_-_detail_03.jpg/1280px-Frescos_from_Sant_Climent_de_Ta%C3%BCll_-_detail_03.jpg"

def search_wikimedia(query):
    print(f"Recherche ciblée sur Wikimedia pour : {query}")
    
    # On utilise l'API standard mais on demande l'URL de l'image (pas la page)
    # On ajoute une taille de miniature élevée pour forcer une bonne qualité si l'original est énorme
    search_url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": query + " filetype:bitmap", "gsrnamespace": "6", "gsrlimit": "20", # On demande plus de résultats
        "prop": "imageinfo", "iiprop": "url|extmetadata|size",
        "iiurlwidth": "2000" # On demande une version de 2000px de large minimum
    })
    
    req = urllib.request.Request(search_url, headers={'User-Agent': 'TalDiaBot/1.0 (contact@taldiacomohoy.com)'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.load(response)
            
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            info = page.get("imageinfo", [{}])[0]
            ext = info.get("extmetadata", {})
            license_short = ext.get("LicenseShortName", {}).get("value", "")
            width = info.get("width", 0)
            
            # On ne garde que le Domaine Public ou CC0, et on vérifie la largeur
            if ("Public domain" in license_short or "CC0" in license_short) and width >= 1000:
                # On préfère l'URL de la miniature de 2000px si elle existe, sinon l'original
                image_url = info.get("thumburl") or info.get("url")
                return image_url
    except Exception as e:
        print(f"Erreur recherche Wikimedia: {e}")
    return None

def get_local_image(assets_dir, last_image):
    images = list(assets_dir.glob("*.jpg"))
    if not images:
        return None
    candidates = [img for img in images if img.name != last_image]
    if not candidates:
        candidates = images
    return random.choice(candidates)

def download_image(url, output_path):
    req = urllib.request.Request(url, headers={'User-Agent': 'TalDiaBot/1.0'})
    try:
        with urllib.request.urlopen(req) as response, open(output_path, 'wb') as out_file:
            out_file.write(response.read())
        return True
    except Exception as e:
        print(f"❌ Erreur téléchargement : {e}")
        return False

if __name__ == "__main__":
    json_file = sys.argv[1]
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 1. On cible la recherche sur le Hook (l'accroche) qui est plus précise
    hook = data.get("hook", "")
    # On nettoie un peu le hook pour enlever les dates et garder le sujet
    query = hook.replace("Tal día como hoy", "").replace("¿Sabías que", "").strip()
    if not query:
        query = "historia de España"
        
    media_dir = pathlib.Path("media")
    media_dir.mkdir(exist_ok=True)
    final_path = media_dir / "image_01.jpg"
    
    # 2. On tente Wikimedia
    image_url = search_wikimedia(query)
    
    if image_url:
        print(f"✅ Image trouvée sur Wikimedia (haute résolution).")
        if download_image(image_url, final_path):
            data["media"] = [{"path": str(final_path)}]
            pathlib.Path(json_file).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            sys.exit(0)

    # 3. Si Wikimedia échoue, on pioche dans la banque locale (si elle existe)
    print("⚠️ Wikimedia n'a rien donné. Recherche dans la banque locale...")
    assets_dir = pathlib.Path("assets/history")
    
    last_image_file = pathlib.Path("last_image.txt")
    last_image = last_image_file.read_text().strip() if last_image_file.exists() else ""
    
    local_img = get_local_image(assets_dir, last_image)
    
    if local_img:
        print(f"✅ Image locale sélectionnée : {local_img.name}")
        shutil.copy(local_img, final_path)
        last_image_file.write_text(local_img.name)
        data["media"] = [{"path": str(final_path)}]
        pathlib.Path(json_file).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        sys.exit(0)
        
    # 4. Si tout échoue, on utilise le fallback ultime
    print("⚠️ Aucune image locale. Utilisation du fallback.")
    if download_image(FALLBACK_URL, final_path):
        data["media"] = [{"path": str(final_path)}]
        pathlib.Path(json_file).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        sys.exit(0)
        
    sys.exit(1)
