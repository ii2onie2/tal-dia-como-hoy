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
        "media_prompt": {"type": "string"}, "series_name": {"type": "string", "description": "Nom de la série (ex: Los Secretos de Goya, Un Día en la Historia)"}
    },
    "required": ["date", "hook", "narration", "caption", "hashtags", "media_prompt"]
}

def get_series_name(format_type):
    if format_type == "date":
        return "Un Día en la Historia"
    elif format_type == "sabias":
        return "¿Sabías que...?"
    else:
        return "El Detalle que Casi Nadie Ve"

def generer_contenu(format_type):
    series_name = get_series_name(format_type)
    print(f"Génération du script ({format_type})...")
    
    if format_type == "date":
        today = datetime.datetime.now()
        mois_espagnol = {
            1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
            5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
            9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
        }
        date_espagnole = f"{today.day} de {mois_espagnol[today.month]}"
        
        prompt_system = f"""Eres un historiador experto para el canal de TikTok "Tal Día Como Hoy".
        Hoy es {date_espagnole}. 
        Encuentra un evento histórico REAL que ocurrió EXACTAMENTE un {date_espagnole} en España.
        Si no encuentras un evento para esa fecha exacta, elige el más cercano posible en la misma semana.
        El guion debe empezar OBLIGATORIAMENTE por "Tal día como hoy, {date_espagnole}...". El hook debe ser una frase que muestre el resultado o el enjeu antes de la explicación (Outcome-first) o incluya un chiffre preciso (Specific number). Ejemplos: "Tal día como hoy, un secreto de la Inquisición cambió la historia de España" o "Tal día como hoy, 14 frescos y 6 meses de trabajo ocultaban un misterio". El hook debe ser una pregunta o afirmación choc que obligue a ver el video.
        La narración debe tener entre 240 y 270 palabras (obligatorio, para superar 1 minuto 12 segundos).
        NO inventes eventos."""
    elif format_type == "sabias":
        prompt_system = """Eres un creador de contenido viral para "Tal Día Como Hoy".
        Crea un guion sobre una curiosidad histórica real y sorprendente sobre España.
        Empieza OBLIGATORIAMENTE por "¿Sabías que...?". El hook debe incluir un chiffre preciso o un fait surprenant (Specific number). Ejemplo: "¿Sabías que Goya pintó 14 frescos en 6 meses?" o "¿Sabías que 3 palabras cambiaron la historia de España?". El hook debe ser una curiosidad sorprendente.
        La narración debe tener entre 240 y 270 palabras (obligatorio, para superar 1 minuto 12 segundos)."""
    else: 
        prompt_system = """Eres un creador de contenido de misterio histórico para "Tal Día Como Hoy".
        Crea un guion sobre un detalle histórico real, poco conocido y fascinante sobre España.
        Empieza OBLIGATORIAMENTE por "El detalle que casi nadie ve...". El hook debe plantear un mystère avec un enjeu clair (Outcome-first). Ejemplo: "El detalle que casi nadie ve en la Alhambra podría cambiar lo que sabemos del arte nazarí" o "El detalle que casi nadie ve en este cuadro esconde una historia de traición". El hook debe ser un misterio intrigante.
        La narración debe tener entre 240 y 270 palabras (obligatorio, para superar 1 minuto 12 segundos)."""

    prompt_system += """
    REGLAS ADICIONALES:
    - El gancho (hook) debe ser una frase corta e impactante.
    - Para media_prompt, encuentra palabras clave en INGLÉS para buscar una pintura histórica.
    - Devuelve el JSON exacto."""

    try:
        response = ollama.chat(
            model='llama3.2:3b',  # ou 'llama3.2:3b' si qwen ne fonctionne pas
            messages=[
                {'role': 'system', 'content': prompt_system},
                {'role': 'user', 'content': 'Génère le script pour cette vidéo.'}
            ],
            format=schema,
            options={'temperature': 0.7}
        )
        data = json.loads(response['message']['content'])
        
        # Vérification de la longueur
        mots = len(data['narration'].split())
        print(f"Longueur de la narration : {mots} mots.")
        if mots < 230:
            print("⚠️ Texte trop court, on ajoute une conclusion pour rallonger.")
            data['narration'] += " Si te ha gustado esta historia, no olvides seguirnos para descubrir cada día un nuevo episodio de la historia de España. ¡Nos vemos en el próximo vídeo!"
            
        data["series_name"] = series_name
        return data
    except Exception as e:
        print(f"\n❌ ERREUR OLLAMA : {e}\n")
        sys.exit(1)

def sauvegarder_json(data, nom_fichier):
    json_final = {
        "date": data["date"],
        "series": data.get("series_name", "Tal Día Como Hoy"),
        "hook": data["hook"],
        "narration": data["narration"],
        "caption": data["caption"],
        "hashtags": data["hashtags"],
        "media": [],
        "format": "chronological_event",
        "duration_target": "75-90s"
    }
    chemin = Path(nom_fichier)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(json_final, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Fichier sauvegardé : {chemin}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
        
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
