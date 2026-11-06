import sys
import json
import pathlib
import random
import shutil

def get_best_image(narration, hook):
    assets_dir = pathlib.Path("assets/history")
    tags_file = pathlib.Path("image_tags.json")
    
    if not tags_file.exists():
        print("❌ image_tags.json introuvable. Sélection au hasard.")
        images = list(assets_dir.glob("*.jpg"))
        return random.choice(images) if images else None
        
    image_tags = json.loads(tags_file.read_text(encoding="utf-8"))
    text_to_search = (narration + " " + hook).lower()
    
    # Dictionnaire de traduction (Espagnol -> Anglais)
    translations = {
        "espada": "sword", "rey": "king", "reina": "queen",
        "batalla": "battle", "castillo": "castle", "iglesia": "cathedral",
        "barco": "ship", "muerte": "death", "oro": "gold", "libro": "book",
        "pintura": "painting", "retrato": "portrait", "soldado": "soldier",
        "guerra": "war", "corona": "crown", "inquisicion": "inquisition",
        "teatro": "theater", "palacio": "palace", "biblioteca": "library",
        "mosaico": "mosaic", "olimpiadas": "olympics", "dios": "god"
    }
    
    search_terms = []
    for es_word, en_word in translations.items():
        if es_word in text_to_search:
            search_terms.append(en_word)

    best_match = None
    max_matches = 0
    
    for img_name, tags in image_tags.items():
        # On ignore les images non taguées (history)
        if tags.strip() == "history":
            continue
            
        if not (assets_dir / img_name).exists():
            continue
            
        current_matches = 0
        for term in search_terms:
            if term in tags:
                current_matches += 1
                
        if current_matches > max_matches:
            max_matches = current_matches
            best_match = img_name

    if best_match:
        selected = assets_dir / best_match
        print(f"✅ Image correspondante trouvée : {selected.name} (Tags: {image_tags[selected.name]})")
    else:
        images = list(assets_dir.glob("*.jpg"))
        selected = random.choice(images)
        print(f"⚠️ Aucune correspondance exacte. Image au hasard : {selected.name}")
        
    return selected

def update_json(json_path, image_path):
    path = pathlib.Path(json_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    
    media_dir = pathlib.Path("media")
    media_dir.mkdir(exist_ok=True)
    final_path = media_dir / "image_01.jpg"
    
    shutil.copy(image_path, final_path)
    
    data["media"] = [{"path": str(final_path)}]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("✅ JSON mis à jour.")

if __name__ == "__main__":
    json_file = sys.argv[1]
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    narration = data.get("narration", "")
    hook = data.get("hook", "")
    
    image_path = get_best_image(narration, hook)
    
    if image_path:
        update_json(json_file, image_path)
    else:
        print("❌ Impossible de trouver une image. Arrêt.")
        sys.exit(1)
