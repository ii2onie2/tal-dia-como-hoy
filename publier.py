import sys, json, os, requests

BUFFER_API_KEY = os.environ.get("BUFFER_API_KEY")
CHANNELS = {
    "tal": "6ae072482f1f5ed648e82143",
    "perro": "6ae072482f1f5ed648e82144"
}

def publier(chaîne, json_path, url_video):
    if not BUFFER_API_KEY:
        print("Erreur : BUFFER_API_KEY manquante.")
        sys.exit(1)

    channel_id = CHANNELS.get(chaîne)
    if not channel_id:
        print(f"Erreur : chaîne '{chaîne}' inconnue.")
        sys.exit(1)

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Erreur lecture JSON : {e}")
        sys.exit(1)

    # Lecture du texte (narration ou caption)
    caption = data.get("caption") or data.get("narration") or data.get("script") or ""
    
    # Ajout des hashtags si présents
    hashtags = data.get("hashtags", "#TalDíaComoHoy #Historia #España")
    texte_final = f"{caption}\n\n{hashtags}".strip()
    texte_final_escaped = texte_final.replace('"""', '\\"\\"\\"')

    # Requête GraphQL Buffer
    query = f"""
    mutation {{
      createPost(input: {{
        channelId: "{channel_id}",
        text: """{texte_final_escaped}""",
        schedulingType: automatic,
        assets: {{
          video: {{
            url: "{url_video}"
          }}
        }}
      }}) {{
        ... on PostActionSuccess {{
          post {{
            id
            status
            dueAt
          }}
        }}
        ... on MutationError {{
          message
        }}
      }}
    }}
    """

    headers = {
        "Authorization": f"Bearer {BUFFER_API_KEY}",
        "Content-Type": "application/json"
    }

    print(f"Envoi à Buffer (chaîne: {chaîne})...")
    response = requests.post("https://api.bufferapp.com/1/graphql", json={"query": query}, headers=headers)

    if response.status_code == 200:
        print("✅ Succès :", response.json())
    else:
        print(f"❌ Erreur Buffer (HTTP {response.status_code}) : {response.text}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python publier.py <tal|perro> <json_path> <url_video>")
        sys.exit(1)
    
    publier(sys.argv[1], sys.argv[2], sys.argv[3])
