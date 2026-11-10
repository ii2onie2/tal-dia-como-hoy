import sys, json, os, datetime, requests

def get_format():
    h = datetime.datetime.utcnow().hour
    if h < 10: return "date"
    elif h < 16: return "sabias"
    else: return "detail"

def call_ollama(prompt):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3.2:3b",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.7}
    }
    try:
        r = requests.post(url, json=payload, timeout=300)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        print(f"Erreur Ollama: {e}")
        return ""

def main():
    if len(sys.argv) < 2:
        print("Usage: python generer_script.py <output.json>")
        return

    output_file = sys.argv[1]
    fmt = get_format()
    print(f"Heure UTC : {datetime.datetime.utcnow().hour}h. Format choisi : {fmt}")

    # Règle absolue pour éviter le crash de Piper
    rules = "RÈGLE ABSOLUE : N'utilise AUCUN mot en anglais, AUCUN symbole mathématique, AUCUNE émoticône. Écris uniquement en espagnol simple et littéraire, avec des phrases courtes. N'utilise pas de caractères spéciaux, uniquement des lettres, des chiffres et de la ponctuation de base (virgule, point, point d'interrogation, point d'exclamation)."

    if fmt == "date":
        prompt = f"Tu es un historien. Écris une narration pour TikTok sur un événement historique survenu le {datetime.date.today().strftime('%d/%m')} en Espagne. Sois captivant. {rules}"
    elif fmt == "sabias":
        prompt = f"Tu es un vulgarisateur. Écris une narration TikTok '¿Sabías que...?' sur un fait surprenant de l'histoire espagnole. Sois captivant. {rules}"
    else:
        prompt = f"Tu es un conteur. Écris une narration TikTok 'El detalle que casi nadie ve...' sur un détail méconnu de l'histoire espagnole. Sois captivant. {rules}"

    print("Génération du script...")
    text = call_ollama(prompt)

    if not text:
        text = "No se pudo generar el texto. Inténtalo de nuevo más tarde."

    # Nettoyage supplémentaire du texte
    text = text.replace('"', "'").replace('“', "'").replace('”', "'").replace('’', "'")
    
    data = {
        "narration": text,
        "series_name": "Tal Día Como Hoy",
        "hook": "Descubre la historia",
        "date": datetime.date.today().strftime("%Y-%m-%d")
    }

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Fichier sauvegardé : {output_file}")

if __name__ == "__main__":
    main()
