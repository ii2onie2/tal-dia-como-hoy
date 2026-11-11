import sys, json, pathlib, random, shutil, os

def get_recent_images():
    history_file = pathlib.Path("last_images.txt")
    if history_file.exists():
        return history_file.read_text(encoding="utf-8").splitlines()[-10:]
    return []

def add_to_history(image_name):
    history_file = pathlib.Path("last_images.txt")
    recent = get_recent_images()
    recent.append(image_name)
    history_file.write_text("\n".join(recent[-10:]), encoding="utf-8")

def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_image.py <json_path>")
        return

    json_path = sys.argv[1]
    assets_dir = pathlib.Path("assets/history")
    media_dir = pathlib.Path("media")
    media_dir.mkdir(exist_ok=True)
    final_path = media_dir / "image_01.jpg"

    if not assets_dir.exists():
        print("❌ Erreur : dossier assets/history introuvable.")
        sys.exit(1)

    # Récupérer toutes les images disponibles
    all_images = [f for f in assets_dir.iterdir() if f.suffix.lower() in ('.jpg', '.jpeg', '.png')]
    if not all_images:
        print("❌ Erreur : aucune image trouvée dans assets/history.")
        sys.exit(1)

    # Filtrer les images déjà utilisées
    recent = get_recent_images()
    available = [img for img in all_images if img.name not in recent]

    if not available:
        print("⚠️ Toutes les images ont été utilisées récemment. On réinitialise l'historique.")
        available = all_images

    # Choisir une image au hasard parmi celles qui restent
    selected = random.choice(available)
    print(f"✅ Image choisie : {selected.name}")

    # Copier l'image vers media/image_01.jpg
    shutil.copy(selected, final_path)
    print(f"✅ Image copiée vers {final_path}")

    # Mettre à jour le fichier JSON avec le chemin de l'image
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["image"] = str(final_path)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ JSON mis à jour avec l'image.")
    except Exception as e:
        print(f"❌ Erreur lecture/écriture JSON : {e}")
        sys.exit(1)

    # Ajouter l'image à l'historique
    add_to_history(selected.name)

if __name__ == "__main__":
    main()
