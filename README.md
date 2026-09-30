# Tal Día Como Hoy

Chaîne de production gratuite pour générer des vidéos verticales destinées au compte TikTok @taldiacomohoy09.

## Architecture

ChatGPT / contenu vérifié -> GitHub -> GitHub Actions -> Piper TTS -> FFmpeg -> MP4 1080x1920 -> publication via Metricool.

## Principes

- aucun VPS requis
- aucun abonnement vidéo payant
- aucune dépendance à Descript
- narration en espagnol d'Espagne
- sous-titres incrustés
- médias Wikimedia Commons ou domaine public avec crédits conservés
- sujets historiques sensibles/politiques traités de façon factuelle et sourcée

## Déclenchement

Le rendu démarre automatiquement lorsqu'un fichier `content/YYYY-MM-DD.json` est ajouté ou modifié.
Un lancement manuel reste également disponible depuis GitHub Actions.

## Voix

Le workflow utilise le modèle Piper `es_ES-sharvard-medium` (espagnol d'Espagne), hébergé dans le dépôt public `rhasspy/piper-voices`.

## Sortie

Le workflow produit :
- `video.mp4`
- `subtitles.srt`
- `caption.txt`
- `sources.json`
- `credits.json`

Le paquet est conservé comme artifact GitHub pendant 30 jours.
