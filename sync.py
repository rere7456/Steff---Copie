import os
import json
import csv
import datetime
import urllib.parse
import time

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
    descriptions_db = {}

    for cat in CATEGORIES:
        img_dir = os.path.join('images', cat)
        if not os.path.exists(img_dir): continue
            
        for filename in sorted(os.listdir(img_dir)):
            if filename.lower().endswith(IMG_EXTENSIONS):
                if filename in existing_data:
                    row = existing_data[filename]
                    row['Categorie'] = cat
                else:
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
                
                safe_filename = urllib.parse.quote(filename)
                img_path = f"images/{cat}/{safe_filename}"
                
                gallery_config.append({
                    "id": filename,
                    "category": cat,
                    "src": img_path,
                    "title": row['Titre'],
                    "year": row['Annee']
                })
                descriptions_db[filename] = row['Description']

    save_csv(final_rows)

    version = int(time.time())

    with open('js/gallery_config.js', 'w', encoding='utf-8') as f:
        f.write(f"const GALLERY_VERSION = {version};\n")
        f.write(f"const GALLERY_ITEMS = {json.dumps(gallery_config, indent=2, ensure_ascii=False)};")
    
    with open('data/descriptions.json', 'w', encoding='utf-8') as f:
        json.dump(descriptions_db, f, indent=2, ensure_ascii=False)

    print(f"✅ Synchro terminée. Images et descriptions séparées pour plus de stabilité.")

if __name__ == "__main__":
    sync()