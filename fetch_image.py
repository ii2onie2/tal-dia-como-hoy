import sys
import json
import urllib.request
import urllib.parse
import pathlib
import os
import base64
import requests

# URL de secours au cas où Gemini échoue
FALLBACK_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/La_rendici%C3%B3n_de_Bail%C3%A9n.jpg/1280px-La_rendici%C3%B3n_de_Bail%C3%A9n.jpg"

def generate_with_gemini(prompt, output_path):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("⚠️ Pas de clé GEMINI_API_KEY trouvée.")
        return False
    
    # On utilise le modèle Nano Banana (Gemini 2.5 Flash Image)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{"text": f"Genera una ilustración histórica vertical (formato 9:16) sobre: {prompt}. Estilo pintura clásica, sin texto."}]
        }]
    }
    
    print("Appel à l'API Gemini pour générer l'image...")
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        data = response.json()
        
        # On cherche l'image dans la réponse
        for part in data["candidates"][0]["content"]["parts"]:
            if "inlineData" in part:
                img_data = base64.b64decode(part["inlineData"]["data"])
                with open(output_path, "wb") as f:
                    f.write(img_data)
                print(f"✅ Image générée par Gemini et sauvegardée dans {output_path}")
                return True
                
        print("❌ Gemini n'a pas renvoyé d'image.")
        return False
    except Exception as e:
        print(f"❌ Erreur API Gemini : {e}")
        return False

def download_fallback(image_url, output_path):
    print(f"Téléchargement de l'image de secours : {image_url}")
    req = urllib.request.Request(image_url, headers={'User-Agent': 'TalDiaBot/1.0'})
    with urllib.request.urlopen(req) as response, open(output_path, 'wb') as out_file:
        out_file.write(response.read())
    return True

def update_json(json_path, image_path):
    path = pathlib.Path(json_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["media"] = [{"path": str(image_path)}]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    json_file = sys.argv[1]
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    prompt = data.get("media_prompt", "historia de España")
    
    media_dir = pathlib.Path("media")
    media_dir.mkdir(exist_ok=True)
    image_path = media_dir / "image_01.jpg"
    
    # 1. On essaie Gemini
    success = generate_with_gemini(prompt, image_path)
    
    # 2. Si Gemini échoue, on prend l'image de secours
    if not success:
        print("Bascule sur l'image de secours (Wikimedia).")
        download_fallback(FALLBACK_URL, image_path)
    
    update_json(json_file, image_path)
    print("✅ JSON mis à jour avec le chemin de l'image.")
