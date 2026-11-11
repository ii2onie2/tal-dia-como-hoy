import sys, json, os, datetime, requests, random

def get_format():
    # On force l'heure UTC pour éviter les décalages
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    h = now_utc.hour
    
    # Logique stricte pour les 3 créneaux
    if h < 12: 
        return "date"      # 7h UTC -> 8h/9h Madrid -> Tal Día Como Hoy
    elif h < 16: 
        return "sabias"    # 14h UTC -> 15h/16h Madrid -> ¿Sabías que...?
    else: 
        return "detail"    # 18h UTC -> 19h/20h Madrid -> El detalle

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
    print(f"Heure UTC : {datetime.datetime.now(datetime.timezone.utc).hour}h. Format choisi : {fmt}")

    # Règles absolues : voix propre + durée minimale (150 mots = ~1m15)
    rules = (
        "RÈGLE ABSOLUE 1 : N'utilise AUCUN mot en anglais, AUCUN symbole mathématique, AUCUNE émoticône. "
        "Écris uniquement en espagnol simple et littéraire, avec des phrases courtes.\n"
        "RÈGLE ABSOLUE 2 : La narration DOIT faire au moins 150 mots pour durer plus d'1 minute 15. "
        "Développe les faits, donne des détails, raconte une petite histoire."
    )

    if fmt == "date":
        # Sujet : Événement historique du jour (on utilise la date du jour)
        today_str = datetime.date.today().strftime('%d/%m')
        prompt = f"Tu es un historien. Écris une narration pour TikTok sur un événement historique survenu le {today_str} en Espagne. Sois captivant. {rules}"
        series_name = "Tal Día Como Hoy"
    elif fmt == "sabias":
        # Sujet : Anecdote / Curiosité (on force un thème différent de l'événement du jour)
        prompt = f"Tu es un vulgarisateur. Écris une narration TikTok '¿Sabías que...?' sur une anecdote historique étonnante, une curiosité ou un fait peu connu de l'histoire de l'Espagne. Ne parle PAS de l'événement principal du jour, choisis un autre sujet. Sois captivant. {rules}"
        series_name = "¿Sabías que...?"
    else:
        # Sujet : Détail méconnu (monument, œuvre, tradition)
        prompt = f"Tu es un conteur. Écris une narration TikTok 'El detalle que casi nadie ve...' sur un détail historique méconnu, caché dans un monument, une œuvre d'art ou une tradition espagnole. Ne parle PAS de l'événement principal du jour, choisis un autre sujet. Sois captivant. {rules}"
        series_name = "El detalle que casi nadie ve"

    print("Génération du script...")
    text = call_ollama(prompt)

    if not text:
        text = "No se pudo generar el texto. Inténtalo de nuevo más tarde."

    # Nettoyage
    text = text.replace('"', "'").replace('“', "'").replace('”', "'").replace('’', "'")

    # Forcer une longueur minimale
    if len(text.split()) < 120:
        print("⚠️ Texte trop court, on ajoute une conclusion pour rallonger.")
        text += "\n\nEn resumen, este es uno de los episodios más fascinantes de la historia de España."

    data = {
        "narration": text,
        "series_name": series_name,
        "hook": "Descubre la historia",
        "date": datetime.date.today().strftime("%Y-%m-%d")
    }

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Fichier sauvegardé : {output_file}")

if __name__ == "__main__":
    main()
