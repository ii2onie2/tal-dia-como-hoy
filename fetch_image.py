import sys
import json
import urllib.request
import urllib.parse
import pathlib

# URL de secours : une fresque romane espagnole célèbre (Sant Climent de Taüll)
FALLBACK_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Frescos_from_Sant_Climent_de_Ta%C3%BCll_-_detail_03.jpg/1280px-Frescos_from_Sant_Climent_de_Ta%C3%BCll_-_detail_03.jpg"

def get_fresco_url(query):
    # On force la recherche sur "fresco" et "Spain" pour avoir des fresques
    search_query = f"{query} fresco Spain filetype:bitmap"
    
    search_url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": search_query, "gsrnamespace": "6", "gsrlimit": "15",
        "prop": "imageinfo", "iiprop": "url|extmetadata|size"
    })
    
    req = urllib.request.Request(search_url, headers={'User-Agent': 'TalDiaBot/1.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.load(response)
            
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            info = page.get("imageinfo", [{}])[0]
            ext = info.get("extmetadata", {})
            license_short = ext.get("LicenseShortName", {}).get("value", "")
            width = info.get("width", 0)
            
            # On ne garde que les images libres ET de bonne qualité (largeur > 1000px)
            if ("Public domain" in license_short or "CC0" in license_short) and width >= 1000:
                return info.get("url")
    except Exception as e:
        print(f"Erreur recherche Wikimedia: {e}")
    return None

def download_and_update(json_path, image_url):
    path = pathlib.Path(json_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    media_dir = pathlib.Path("media")
    media_dir.mkdir(exist_ok=True)
    image_path = media_dir / "image_01.jpg"
    
    print(f"Téléchargement de la fresque : {image_url}")
    req = urllib.request.Request(image_url, headers={'User-Agent': 'TalDiaBot/1.0'})
    try:
        with urllib.request.urlopen(req) as response, open(image_path, 'wb') as out_file:
            out_file.write(response.read())
        data["media"] = [{"path": str(image_path)}]
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print("✅ JSON mis à jour avec une seule fresque de haute qualité.")
        return True
    except Exception as e:
        print(f"❌ Erreur téléchargement : {e}")
        return False

if __name__ == "__main__":
    json_file = sys.argv[1]
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # On récupère le prompt généré par Ollama, mais on le modifie pour cibler les fresques
    prompt = data.get("media_prompt", "history Spain")
    print(f"Recherche de fresque pour : {prompt}")
    
    image_url = get_fresco_url(prompt)
    
    if not image_url:
        print("⚠️ Aucune fresque trouvée, utilisation de l'image de secours.")
        image_url = FALLBACK_URL
        
    if not download_and_update(json_file, image_url):
        sys.exit(1)
