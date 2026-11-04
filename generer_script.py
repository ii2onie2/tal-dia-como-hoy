import sys
import json
import ollama
import datetime
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

def generer_contenu(format_type):
    print(f"Génération du script pour le format : {format_type}...")
    
    if format_type == "date":
        prompt_system = """Eres un historiador experto para el canal de TikTok "Tal Día Como Hoy".
        Inventa un evento histórico real que ocurrió en una fecha de hoy (o muy cercana) en España.
        Tu guion debe empezar OBLIGATORIAMENTE por "Tal día como hoy...".
        El tono debe ser narrativo y cautivador."""
    elif format_type == "sabias":
        prompt_system = """Eres un creador de contenido viral para el canal "Tal Día Como Hoy".
        Inventa una curiosidad o anécdota histórica real y sorprendente sobre España.
        Tu guion debe empezar OBLIGATORIAMENTE por "¿Sabías que...?".
        El tono debe ser rápido y sorprendente."""
    else: 
        prompt_system = """Eres un creador de contenido de misterio histórico para el canal "Tal Día Como Hoy".
        Inventa un detalle histórico real, poco conocido y fascinante sobre la historia de España.
        Tu guion debe empezar OBLIGATORIAMENTE por "El detalle que casi nadie ve...".
        El tono debe ser misterioso y revelador."""

    prompt_system += """
    REGLAS ESTRICTAS:
    - La narración debe estar en español y tener unas 120-150 palabras.
    - El gancho (hook) debe ser una frase corta e impactante para TikTok.
    - Para media_prompt, encuentra palabras clave en INGLÉS para buscar una pintura histórica (ej: "Goya Dos de Mayo painting").
    - Devuelve el JSON exacto."""

    try:
        response = ollama.chat(
            model='llama3.2:3b',
            messages=[
                {'role': 'system', 'content': prompt_system},
                {'role': 'user', 'content': 'Génère le script pour cette vidéo.'}
            ],
            format=schema,
            options={'temperature': 0.9} # Un peu de créativité pour varier les sujets
        )
        return json.loads(response['message']['content'])
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
        "duration_target": "65-80s"
    }
    chemin = Path(nom_fichier)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(json_final, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Fichier sauvegardé : {chemin}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
        
    # On détermine le format selon l'heure UTC
    heure = datetime.datetime.now(datetime.timezone.utc).hour
    
    if heure < 10:
        target_format = "date"
    elif heure < 16:
        target_format = "sabias"
    else:
        target_format = "detail"
        
    print(f"Heure UTC : {heure}h. Format choisi : {target_format}")
    
    data = generer_contenu(target_format)
    sauvegarder_json(data, sys.argv[1])
