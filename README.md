# Flegrei RSS

Générateur de flux RSS pour les séismes des Campi Flegrei à partir des données publiques de l'INGV.

## Fonctionnement

Le script :

- télécharge `events.json`
- détecte les nouveaux événements
- génère `feed.xml`
- sauvegarde l'état dans `state.json`

GitHub Actions exécute automatiquement le script toutes les 15 minutes.

## Installation locale

```bash
pip install -r requirements.txt
python generate_rss.py
```

Le fichier `feed.xml` est créé à la racine du projet.

## GitHub Actions

Le workflow se trouve dans :

```
.github/workflows/update.yml
```

Il peut être lancé :

- automatiquement (cron)
- manuellement depuis l'onglet **Actions**

## GitHub Pages

Activer :

Settings → Pages

Source :

```
Deploy from a branch
```

Branch :

```
main
```

Folder :

```
/ (root)
```

Le flux sera alors disponible à :

```
https://ialyon69000-dev.github.io/flegrei-rss/feed.xml
```

## Dépendances

- requests
- feedgen
- beautifulsoup4
- lxml

## Source des données

https://terremoti.ov.ingv.it/gossip/flegrei/2026/events.json
