import sys
import json
import ollama
from pathlib import Path

# Le schéma JSON que l'IA doit respecter
schema = {
    "type": "object",
    "properties": {
        "date": {"type": "string", "description": "Date de l'événement au format YYYY-MM-DD"},
        "hook": {"type": "string", "description": "Accroche courte (max 10 mots), commençant par la date"},
        "narration": {"type": "string", "description": "Texte complet à lire en espagnol (environ 120-150 mots)"},
        "caption": {"type": "string", "description": "Texte du post TikTok en espagnol avec les crédits des images"},
        "hashtags": {"type": "array", "items": {"type": "string"}},
        "media_prompt": {"type": "string", "description": "Mots-clés en anglais pour chercher des peintures historiques sur Wikimedia Commons"}
    },
    "required": ["date", "hook", "narration", "caption", "hashtags", "media_prompt"]
}

def generer_contenu(sujet):
    print(f"Génération du script pour : {sujet}... (ça peut prendre 30 secondes)")
    
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
            model='jobautomation/OpenEuroLLM-Spanish',
            messages=[
                {'role': 'system', 'content': prompt_system},
                {'role': 'user', 'content': f'Génère le script pour le sujet suivant : {sujet}'}
            ],
            format=schema, # On impose la structure JSON
            options={'temperature': 0.0} # Résultat déterministe
        )
        
        contenu = json.loads(response['message']['content'])
        return contenu

    except Exception as e:
        print("Erreur lors de la génération :", e)
        sys.exit(1)

def sauvegarder_json(data, nom_fichier):
    json_final = {
        "date": data["date"],
        "series": "Tal Día Como Hoy",
        "hook": data["hook"],
        "narration": data["narration"],
        "caption": data["caption"],
        "hashtags": data["hashtags"],
        "media": [], # À remplir plus tard
        "format": "chronological_event",
        "hook_pattern": "date_first",
        "duration_target": "65-80s"
    }
    
    chemin = Path("content") / nom_fichier
    chemin.parent.mkdir(exist_ok=True)
    chemin.write_text(json.dumps(json_final, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Fichier sauvegardé : {chemin}")
    print(f"🔍 Mot-clé pour les images : {data['media_prompt']}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generer_script.py <sujet> <nom_fichier.json>")
        sys.exit(1)
        
    sujet = sys.argv[1]
    nom_fichier = sys.argv[2]
    
    data = generer_contenu(sujet)
    sauvegarder_json(data, nom_fichier)