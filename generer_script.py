import sys
import json
import ollama
from pathlib import Path

schema = {
    "type": "object",
    "properties": {
        "date": {"type": "string"},
        "hook": {"type": "string"},
        "narration": {"type": "string"},
        "caption": {"type": "string"},
        "hashtags": {"type": "array", "items": {"type": "string"}},
        "media_prompt": {"type": "string"}
    },
    "required": ["date", "hook", "narration", "caption", "hashtags", "media_prompt"]
}

def generer_contenu(sujet):
    print(f"Génération du script pour : {sujet}...")
    prompt_system = """Eres un historiador y redactor para el canal de TikTok español "Tal Día Como Hoy".
Tu objetivo es crear un guion de 60 segundos sobre un evento histórico relacionado con España.
REGLAS:
- La narración debe estar en español, ser cautivadora y tener unas 120-150 palabras.
- Debe empezar por "Tal día como hoy..." y terminar con una pregunta retórica.
- El gancho (hook) debe ser impactante e incluir la fecha.
- Los hashtags deben ser relevantes en español (ej: #HistoriaDeEspaña).
- Para el campo media_prompt, encuentra palabras clave en INGLÉS para buscar una pintura histórica (ej: "Goya Dos de Mayo painting")."""

    try:
        response = ollama.chat(
            model='llama3.2:3b',
            messages=[
                {'role': 'system', 'content': prompt_system},
                {'role': 'user', 'content': f'Génère le script pour le sujet suivant : {sujet}'}
            ],
            format=schema,
            options={'temperature': 0.0}
        )
        contenu = json.loads(response['message']['content'])
        return contenu
    except Exception as e:
        print(f"\n❌ ERREUR OLLAMA : {e}\n")
        sys.exit(1)

def sauvegarder_json(data, nom_fichier):
    json_final = {
        "date": data["date"],
        "series": "Tal Día Como Hoy",
        "hook": data["hook"],
        "narration": data["narration"],
        "caption": data["caption"],
        "hashtags": data["hashtags"],
        "media": [],
        "format": "chronological_event",
        "hook_pattern": "date_first",
        "duration_target": "65-80s"
    }
    chemin = Path(nom_fichier)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(json_final, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Fichier sauvegardé : {chemin}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generer_script.py <sujet> <nom_fichier.json>")
        sys.exit(1)
    data = generer_contenu(sys.argv[1])
    sauvegarder_json(data, sys.argv[2])
