# Relecture sources 21/10 — deuxième version

**PR #6 contient uniquement le contenu : le correctif de sécurité est déjà sur `main` (c97e92f). Aucune PR de sécurité à fusionner.**

**Toutes les cases restent décochées.** Les extraits Hérodote viennent de la vérification du relecteur indépendant ; leur page n'a pas pu être récupérée par l'assistant. Vérifier chaque lien soi-même avant de cocher.

## Affirmations proposées (7 à vérifier)

| Risque / n° | Texte prononcé | Source 1 + extrait | Source 2 + extrait | Statut | Validation |
|---|---|---|---|---|---|
| ⚠️ C03 | Los británicos contaban con veintisiete navíos; la escuadra combinada, con treinta y tres. | [HISTORY / A&E Television Networks](https://www.history.com/articles/battle-of-trafalgar) : « 27 ships ... 33 ships » | [Hérodote](https://www.herodote.net/21_octobre_1805-evenement-18051021.php) : « 27 navires anglais contre 33 franco-espagnols » | À vérifier par le propriétaire | [ ] |
| ⚠️ C04 | Pierre-Charles de Villeneuve mandaba el contingente francés de la flota combinada. | [HISTORY / A&E Television Networks](https://www.history.com/articles/battle-of-trafalgar) : « led by French Vice-Admiral Pierre-Charles de Villeneuve » | [Hérodote](https://www.herodote.net/21_octobre_1805-evenement-18051021.php) : « Villeneuve commande la flotte française » | À vérifier par le propriétaire | [ ] |
| ⚠️ C05 | Horatio Nelson estaba al mando de la flota británica. | [HISTORY / A&E Television Networks](https://www.history.com/articles/battle-of-trafalgar) : « commanded by Admiral Horatio Nelson » | [Hérodote](https://www.herodote.net/21_octobre_1805-evenement-18051021.php) : « Nelson » | À vérifier par le propriétaire | [ ] |
| ⚠️ C07 | Nelson fue herido de muerte durante la batalla. | [HISTORY / A&E Television Networks](https://www.history.com/articles/battle-of-trafalgar) : « he died three hours later » | [Hérodote](https://www.herodote.net/21_octobre_1805-evenement-18051021.php) : « Nelson blessé sur le pont, mort avant de savourer son triomphe » | À vérifier par le propriétaire | [ ] |
|  C01 | El 21 de octubre de 1805 se libró la batalla de Trafalgar. | [HISTORY / A&E Television Networks](https://www.history.com/articles/battle-of-trafalgar) : « October 21, 1805 » | [Hérodote](https://www.herodote.net/21_octobre_1805-evenement-18051021.php) : « Le 21 octobre 1805 » | À vérifier par le propriétaire | [ ] |
|  C02 | Se enfrentaron la flota británica y una escuadra combinada francesa y española. | [HISTORY / A&E Television Networks](https://www.history.com/articles/battle-of-trafalgar) : « combined French-Spanish fleet » | [Hérodote](https://www.herodote.net/21_octobre_1805-evenement-18051021.php) : « les navires espagnols ont rallié Cadix » | À vérifier par le propriétaire | [ ] |
|  C09 | El combate tuvo lugar frente a la costa española, cerca de Cádiz. | [HISTORY / A&E Television Networks](https://www.history.com/articles/battle-of-trafalgar) : « off the southwest coast of Spain » | [Hérodote](https://www.herodote.net/21_octobre_1805-evenement-18051021.php) : « au large du cap Trafalgar, non loin de Cadix » | À vérifier par le propriétaire | [ ] |

## Non retenues : ne pas cocher ni utiliser dans le script

- **C06** — Nelson organizó el ataque británico en dos columnas. — **REMOVED** (SECOND_EDITORIAL_SOURCE_MISSING)
- **C08** — Tras el combate, una tormenta hundió buena parte de los barcos enemigos capturados. — **REMOVED** (SECOND_EDITORIAL_SOURCE_MISSING)
- **C10** — Federico Gravina estaba al mando de la escuadra española. — **PENDING_SECOND_SOURCE** (seconde source indépendante non obtenue)
- **C11** — Cosme Damián de Churruca murió en Trafalgar. — **PENDING_SECOND_SOURCE** (seconde source indépendante non obtenue)

## Script espagnol — version de relecture, NON définitive

« El veintiuno de octubre de mil ochocientos cinco, frente a la costa española, cerca de Cádiz, se libró una batalla naval que marcó la historia de España: Trafalgar.

En un lado combatía la flota británica, bajo el mando de Horatio Nelson. En el otro, una escuadra combinada de Francia y España, con Pierre-Charles de Villeneuve al frente del contingente francés.

Las cifras ayudan a imaginar la escala del enfrentamiento: veintisiete navíos británicos frente a treinta y tres franceses y españoles. No eran unos pocos barcos: dos flotas enteras se enfrentaron aquel veintiuno de octubre.

Nelson, el comandante británico, fue herido de muerte durante la batalla.

Esta fecha recuerda un episodio en el que España combatió junto a Francia contra Gran Bretaña, cerca de la costa de Cádiz. La batalla de Trafalgar sigue siendo una referencia al hablar de la historia naval de aquel año.

¿Conocías estos datos sobre Trafalgar? Cuéntanoslo en los comentarios y sigue Tal Día Como Hoy para descubrir más episodios de nuestra historia. »

**Durée parlée : NON MESURÉE.** Impossible de valider l'objectif 61 à 80 secondes avant génération et examen d'un fichier audio réel. Ce texte n'est pas autorisé au rendu ni prêt pour publication.

## Instructions de vérification
1. PR #6 → **Files changed** → `content/research/REVIEW_SOURCES.md`. Ouvrir les deux liens de chacune des sept lignes ; une citation doit vraiment corroborer le texte espagnol.
2. Éditer les cases `[ ]` vers `[x]` uniquement pour les sept faits correctement corroborés et commenter chaque divergence.
3. Ne pas fusionner la PR : les images, la voix et le rendu restent non validés.

**Critère OK : sept faits vérifiés par deux éditeurs indépendants et aucun fait absent du script. Sinon NON et suppression de la phrase concernée.**
