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

    rules = (
        "RÈGLE ABSOLUE 1 : Écris UNIQUEMENT en espagnol d'Espagne. N'utilise AUCUN mot de français.\n"
        "RÈGLE ABSOLUE 2 : N'utilise AUCUN mot en anglais, AUCUN symbole mathématique, AUCUNE émoticône.\n"
        "RÈGLE ABSOLUE 3 : La narration DOIT faire au moins 150 mots.\n"
        "RÈGLE ABSOLUE 4 : Écris UNIQUEMENT le texte que la voix off doit prononcer. N'inclus AUCUNE indication de mise en scène, AUCUNE description d'image, AUCUNE action entre parenthèses (comme '(Baja la cámara)' ou '(Imágenes de...)')."
    )

    if fmt == "date":
        today_str = datetime.date.today().strftime('%d/%m')
        prompt = f"Eres un historiador español. Escribe una narración para TikTok sobre un evento histórico ocurrido el {today_str} en España. Sé cautivador. {rules}"
        series_name = "Tal Día Como Hoy"
    elif fmt == "sabias":
        prompt = f"Eres un divulgador español. Escribe una narración TikTok '¿Sabías que...?' sobre una anécdota histórica sorprendente. No hables del evento principal del día. Sé cautivador. {rules}"
        series_name = "¿Sabías que...?"
    else:
        prompt = f"Eres un narrador español. Escribe una narración TikTok 'El detalle que casi nadie ve...' sobre un detalle histórico poco conocido, escondido en un monumento o una tradición española. Sé cautivador. {rules}"
        series_name = "El detalle que casi nadie ve"

    print("Génération du script...")
    text = call_ollama(prompt)

    # Boucle de sécurité pour la longueur
    attempts = 0
    while len(text.split()) < 140 and attempts < 3:
        print(f"⚠️ Texte trop court ({len(text.split())} mots). Tentative {attempts+1}/3...")
        if attempts == 0: prompt += " Développe davantage, raconte une histoire complète."
        elif attempts == 1: prompt += " La narration doit absolument faire plus de 150 mots."
        else: prompt += " Fais une narration très détaillée de plus de 200 mots."
        text = call_ollama(prompt)
        attempts += 1

    if is_french(text):
        print("⚠️ Texte en français détecté, régénération en espagnol...")
        text = call_ollama(prompt + " IMPORTANT : Escribe en ESPAÑOL, no en francés.")

    if not text:
        text = "No se pudo generar el texto. Inténtalo de nuevo más tarde."

    # Nettoyage des parenthèses et guillemets
    import re
    text = re.sub(r'\(.*?\)', '', text) # Supprime tout ce qui est entre parenthèses
    text = text.replace('"', "'").replace('“', "'").replace('”', "'").replace('’', "'").strip()

    if len(text.split()) < 120:
        print("⚠️ Texte toujours trop court, on ajoute une conclusion.")
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
