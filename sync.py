import os
import json
import csv
import datetime
import urllib.parse
import time

# Configuration
CATEGORIES = ['mariages', 'nature-paysages', 'reportages', 'urbain', 'creatif']
IMG_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.svg', '.webp')
CSV_FILE = 'data/portfolio.csv'
DETAILS_DIR = 'data/details'

def load_csv():
    data = {}
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                if row.get('Fichier'):
                    data[row['Fichier']] = row
    return data

def save_csv(rows):
    os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)
    with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['Fichier', 'Categorie', 'Titre', 'Annee', 'Description']
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(rows)

def sync():
    existing_data = load_csv()
    final_rows = []
    gallery_config = []
    
    # Création du dossier des fiches individuelles
    if not os.path.exists(DETAILS_DIR):
        os.makedirs(DETAILS_DIR)

    for cat in CATEGORIES:
        img_dir = os.path.join('images', cat)
        if not os.path.exists(img_dir): continue
            
        for filename in sorted(os.listdir(img_dir)):
            if filename.lower().endswith(IMG_EXTENSIONS):
                # 1. Récupération ou création des infos
                if filename in existing_data:
                    row = existing_data[filename]
                    row['Categorie'] = cat
                else:
                    full_path = os.path.join(img_dir, filename)
                    year = datetime.datetime.fromtimestamp(os.path.getmtime(full_path)).strftime('%Y')
                    title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title().replace("é", "e")
                    row = {
                        'Fichier': filename,
                        'Categorie': cat,
                        'Titre': title,
                        'Annee': year,
                        'Description': f"Description pour {title}..."
                    }
                
                final_rows.append(row)
                
                # 2. Encodage du chemin image
                safe_filename = urllib.parse.quote(filename)
                img_path = f"images/{cat}/{safe_filename}"
                
                # 3. Création de la FICHE INDIVIDUELLE (JSON)
                # On utilise un nom de fichier sécurisé pour la fiche
                detail_id = filename.replace(' ', '_').replace("'", "_").replace('é', 'e')
                detail_filename = f"{detail_id}.json"
                
                detail_data = {
                    "title": row['Titre'],
                    "year": row['Annee'],
                    "category": row['Categorie'],
                    "description": row['Description']
                }
                
                with open(os.path.join(DETAILS_DIR, detail_filename), 'w', encoding='utf-8') as f:
                    json.dump(detail_data, f, indent=2, ensure_ascii=False)

                # 4. Config ultra-légère pour la grille
                gallery_config.append({
                    "id": detail_id, # L'ID qui permettra de charger la fiche
                    "category": cat,
                    "src": img_path,
                    "title": row['Titre'] # Titre affiché sous l'image en grille
                })

    save_csv(final_rows)

    version = int(time.time())
    with open('js/gallery_config.js', 'w', encoding='utf-8') as f:
        f.write(f"const GALLERY_VERSION = {version};\n")
        f.write(f"const GALLERY_ITEMS = {json.dumps(gallery_config, indent=2, ensure_ascii=False)};")

    print(f"✅ Synchro terminée. {len(gallery_config)} fiches individuelles créées dans {DETAILS_DIR}")

if __name__ == "__main__":
    sync()
