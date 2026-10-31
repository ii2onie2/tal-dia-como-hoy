# Tal Día Como Hoy

Chaîne de production gratuite pour générer des vidéos verticales destinées au compte TikTok @taldiacomohoy09.

## Architecture

ChatGPT / contenu vérifié -> GitHub -> GitHub Actions -> Piper TTS -> FFmpeg -> MP4 1080x1920 -> programmation et publication via Buffer après contrôles obligatoires.

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

## Buffer — canal de programmation et publication

- Buffer est la seule destination cible de programmation et de publication TikTok pour ce projet.
- La connexion des deux chaînes et l'autorisation de programmation/publication ont été confirmées par le propriétaire.
- La mise en production dépend toujours de contrôles réussis : contenu exact, provenance et droits des médias, crédits, mentions IA, qualité du MP4, détection de doublons et confirmation de l'état distant.
- Ne pas créer de brouillon, programmer ou publier un contenu qui échoue à un contrôle; ne jamais présenter un rendu local comme une publication distante.
- Préserver l'idempotence, tracer les identifiants distants et permettre une reprise sans double publication.
- Aucun secret ou identifiant n'est consigné dans ce dépôt.
