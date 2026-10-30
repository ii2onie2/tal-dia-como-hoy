# Tal Día Como Hoy

Chaîne de production gratuite pour générer des vidéos verticales destinées au compte TikTok @taldiacomohoy09.

## Architecture

ChatGPT / contenu vérifié -> GitHub -> GitHub Actions -> Piper TTS -> FFmpeg -> MP4 1080x1920 -> préparation et validation pour Buffer (publication TikTok uniquement après autorisation distincte).

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

## Buffer et workflow historique

Buffer remplace Metricool comme destination prévue. Les workflows `buffer-readonly-preflight.yml`, `buffer-video-dry-run.yml` et `buffer-public-media-preflight.yml` vérifient la connexion, les fichiers et leur accessibilité sans créer de brouillon ni publier.

Le workflow historique `publish-trypost.yml` est réactivé comme point d'entrée **manuel de préparation Buffer**, sans appel d'écriture à Buffer ni publication TikTok. Il vérifie la présence des trois paquets vidéo, leurs crédits et leurs sources avant toute étape de publication. Une publication réelle nécessite une autorisation distincte, la vérification des droits et un workflow d'envoi explicitement validé.
