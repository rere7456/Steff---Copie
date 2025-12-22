import os
import json
import csv
import datetime
import urllib.parse

# Configuration
CATEGORIES = ['mariages', 'nature-paysages', 'portrait-reportages', 'urbain', 'creatif']
IMG_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.svg', '.webp')
CSV_FILE = 'data/portfolio.csv'

def load_csv():
    data = {}
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                data[row['Fichier']] = row
    return data

def save_csv(rows):
    with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['Fichier', 'Categorie', 'Titre', 'Annee', 'Description']
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(rows)

def sync():
    existing_data = load_csv()
    final_rows = []
    gallery_config = []
    descriptions_db = {}

    for cat in CATEGORIES:
        img_dir = os.path.join('images', cat)
        if not os.path.exists(img_dir): continue
            
        for filename in os.listdir(img_dir):
            if filename.lower().endswith(IMG_EXTENSIONS):
                # 1. Récupération des infos (soit du CSV, soit calculées)
                if filename in existing_data:
                    row = existing_data[filename]
                else:
                    # Nouvelle photo !
                    full_path = os.path.join(img_dir, filename)
                    year = datetime.datetime.fromtimestamp(os.path.getmtime(full_path)).strftime('%Y')
                    title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title().replace("'", "•").replace("é", "e")
                    row = {
                        'Fichier': filename,
                        'Categorie': cat,
                        'Titre': title,
                        'Annee': year,
                        'Description': f"Description pour {title}..."
                    }
                
                final_rows.append(row)
                
                # 2. Données légères pour la grille (sans description)
                img_path = f"images/{cat}/{urllib.parse.quote(filename)}"
                item_id = f"img_{len(gallery_config)}"
                gallery_config.append({
                    "id": item_id,
                    "category": cat,
                    "src": img_path,
                    "title": row['Titre'],
                    "year": row['Annee']
                })
                
                # 3. Base de données des descriptions (chargée plus tard)
                descriptions_db[item_id] = row['Description']

    # Sauvegarde du CSV pour l'utilisateur
    save_csv(final_rows)

    # Export pour le site
    # Fichier 1 : Config de la grille (toujours chargé)
    with open('js/gallery_config.js', 'w', encoding='utf-8') as f:
        f.write(f"const GALLERY_ITEMS = {json.dumps(gallery_config, indent=2, ensure_ascii=False)};")
    
    # Fichier 2 : Descriptions (chargé uniquement au clic)
    with open('data/descriptions.json', 'w', encoding='utf-8') as f:
        json.dump(descriptions_db, f, indent=2, ensure_ascii=False)

    print(f"✅ Synchro terminée : {len(gallery_config)} photos.")
    print(f"👉 Modifiez vos textes dans {CSV_FILE}")

if __name__ == "__main__":
    sync()
