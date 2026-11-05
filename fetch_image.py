import sys
import json
import urllib.request
import urllib.parse
import pathlib
import random
import shutil

# URL de secours STABLE (hébergée sur votre dépôt GitHub)
# On utilisera une image que vous allez créer à l'étape suivante
FALLBACK_URL = "https://raw.githubusercontent.com/ii2onie2/tal-dia-como-hoy/main/assets/history/fallback.jpg"

def search_wikimedia(query):
    print(f"Recherche ciblée sur Wikimedia pour : {query}")
    
    search_url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": query + " filetype:bitmap", "gsrnamespace": "6", "gsrlimit": "10",
        "prop": "imageinfo", "iiprop": "url|extmetadata|size",
        "iiurlwidth": "2000"
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
            
            if ("Public domain" in license_short or "CC0" in license_short) and width >= 800:
                image_url = info.get("thumburl") or info.get("url")
                return image_url
    except Exception as e:
        print(f"Erreur recherche Wikimedia: {e}")
    return None

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
    
    hook = data.get("hook", "")
    
    # 1. On nettoie le hook pour ne garder que les mots-clés (on vire les mots vides)
    stop_words = ["la", "el", "los", "las", "de", "del", "en", "que", "un", "una", "tenía", "¿", "?", ".", ","]
    words = hook.replace("Tal día como hoy", "").replace("¿Sabías que", "").split()
    clean_words = [w for w in words if w.lower() not in stop_words]
    
    # On prend les 4 mots les plus importants pour la recherche
    query = " ".join(clean_words[:4]) 
    if not query:
        query = "historia de España"
        
    media_dir = pathlib.Path("media")
    media_dir.mkdir(exist_ok=True)
    final_path = media_dir / "image_01.jpg"
    
    # 2. On tente Wikimedia
    image_url = search_wikimedia(query)
    
    if image_url:
        print(f"✅ Image trouvée sur Wikimedia.")
        if download_image(image_url, final_path):
            data["media"] = [{"path": str(final_path)}]
            pathlib.Path(json_file).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            sys.exit(0)

    # 3. Si Wikimedia échoue, on utilise le fallback GitHub
    print("⚠️ Wikimedia n'a rien donné. Utilisation du fallback GitHub.")
    if download_image(FALLBACK_URL, final_path):
        data["media"] = [{"path": str(final_path)}]
        pathlib.Path(json_file).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        sys.exit(0)
        
    print("❌ Impossible de récupérer une image. Arrêt.")
    sys.exit(1)
