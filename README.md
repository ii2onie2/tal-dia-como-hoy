# Tal Día Como Hoy

Chaîne de production gratuite pour générer des vidéos verticales destinées au compte TikTok @taldiacomohoy09.

## Architecture

ChatGPT / contenu vérifié -> GitHub -> GitHub Actions -> Piper TTS -> FFmpeg -> MP4 1080x1920 -> préparation pour Buffer (publication désactivée sans autorisation distincte).

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

## Buffer migration / état de publication

- Buffer remplace Metricool comme destination envisagée de planification, sous réserve de validation de la connexion et des droits du compte.
- La génération MP4 et le dépôt des artefacts GitHub ne constituent pas une publication TikTok.
- Aucun appel API Buffer, création de brouillon, programmation ou publication n'est autorisé par cette migration.
- Vérifier manuellement la connexion TikTok/Buffer, les capacités et quotas du compte, puis obtenir une autorisation distincte avant toute action externe.
- Les contrôles éditoriaux, licences, attributions, étiquetage IA et qualité MP4 restent obligatoires.
- Retour arrière : fermer la PR sans fusion, ou revert du commit si fusion ultérieure.
