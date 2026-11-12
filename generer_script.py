import sys, json, os, datetime, requests

def get_format():
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    h = now_utc.hour
    if h < 12: return "date"
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

def is_french(text):
    # Détection basique de mots français courants
    french_words = ["bonjour", "salut", "aujourd'hui", "je ", "vous ", "nous ", "est ", "une ", "des ", "les ", "dans ", "pour "]
    text_lower = text.lower()
    for word in french_words:
        if word in text_lower:
            return True
    return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python generer_script.py <output.json>")
        return

    output_file = sys.argv[1]
    fmt = get_format()
    print(f"Heure UTC : {datetime.datetime.now(datetime.timezone.utc).hour}h. Format choisi : {fmt}")

    # Règle absolue : espagnol uniquement, pas de français, durée minimale
    rules = (
        "RÈGLE ABSOLUE 1 : Écris UNIQUEMENT en espagnol d'Espagne. N'utilise AUCUN mot de français. "
        "Si tu utilises un mot français, la vidéo sera rejetée.\n"
        "RÈGLE ABSOLUE 2 : N'utilise AUCUN mot en anglais, AUCUN symbole mathématique, AUCUNE émoticône.\n"
        "RÈGLE ABSOLUE 3 : La narration DOIT faire au moins 150 mots pour durer plus d'1 minute 15."
    )

    if fmt == "date":
        today_str = datetime.date.today().strftime('%d/%m')
        prompt = f"Eres un historiador español. Escribe una narración para TikTok sobre un evento histórico ocurrido el {today_str} en España. Sé cautivador. {rules}"
        series_name = "Tal Día Como Hoy"
    elif fmt == "sabias":
        prompt = f"Eres un divulgador español. Escribe una narración TikTok '¿Sabías que...?' sobre una anécdota histórica sorprendente, una curiosidad o un hecho poco conocido de la historia de España. No hables del evento principal del día, elige otro tema. Sé cautivador. {rules}"
        series_name = "¿Sabías que...?"
    else:
        prompt = f"Eres un narrador español. Escribe una narración TikTok 'El detalle que casi nadie ve...' sobre un detalle histórico poco conocido, escondido en un monumento, una obra de arte o una tradición española. No hables del evento principal del día, elige otro tema. Sé cautivador. {rules}"
        series_name = "El detalle que casi nadie ve"

    print("Génération du script...")
    text = call_ollama(prompt)

    # Si le texte est en français, on régénère
    if is_french(text):
        print("⚠️ Texte en français détecté, régénération en espagnol...")
        text = call_ollama(prompt + " IMPORTANT : Escribe en ESPAÑOL, no en francés.")

    if not text:
        text = "No se pudo generar el texto. Inténtalo de nuevo más tarde."

    text = text.replace('"', "'").replace('“', "'").replace('”', "'").replace('’', "'")

    if len(text.split()) < 120:
        print("⚠️ Texte trop court, on ajoute une conclusion.")
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
