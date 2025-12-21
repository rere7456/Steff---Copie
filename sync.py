import os
import json
import datetime
import urllib.parse

# Configuration
CATEGORIES = [
    'mariages',
    'nature-paysages',
    'portrait-reportages',
    'urbain',
    'creatif'
]

IMG_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.svg', '.webp')

def parse_txt_file(file_path):
    data = {"date": None, "description": ""}
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                line_str = line.strip()
                if line_str.lower().startswith('date :'):
                    data["date"] = line_str.split(':', 1)[1].strip()
                elif line_str.lower().startswith('description :') or line_str.lower().startswith('descritpion :'):
                    data["description"] = line_str.split(':', 1)[1].strip()
    return data

def generate_catalog():
    catalog = []
    
    for cat in CATEGORIES:
        img_dir = os.path.join('images', cat)
        
        if not os.path.exists(img_dir):
            continue
            
        files = os.listdir(img_dir)
        for filename in files:
            if filename.lower().endswith(IMG_EXTENSIONS):
                basename = os.path.splitext(filename)[0]
                
                # Encodage du chemin pour éviter les problèmes avec les espaces
                # Mais attention, on ne veut pas encoder les '/'
                safe_filename = urllib.parse.quote(filename)
                img_path = f"images/{cat}/{safe_filename}"
                
                desc_rel_path = f"data/{cat}/{basename}.txt"
                full_desc_path = os.path.join('data', cat, f"{basename}.txt")
                
                # --- RÉCUPÉRATION DES INFOS DEPUIS LE TXT ---
                txt_info = parse_txt_file(full_desc_path)
                
                # Date
                year = txt_info["date"]
                if not year:
                    full_img_path = os.path.join('images', cat, filename)
                    timestamp = os.path.getmtime(full_img_path)
                    year = datetime.datetime.fromtimestamp(timestamp).strftime('%Y')
                
                # Description
                description = txt_info["description"]
                
                # --- GÉNÉRATION DU TITRE ---
                title = basename.replace('_', ' ').replace('-', ' ').title()
                title = title.replace("'", "•").replace("é", "e").replace("É", "E")

                # Création automatique du txt si manquant
                if not os.path.exists(full_desc_path):
                    os.makedirs(os.path.dirname(full_desc_path), exist_ok=True)
                    with open(full_desc_path, 'w', encoding='utf-8') as f:
                        f.write(f"date : {year}\n")
                        f.write(f"description : Description pour {title}...")
                    description = f"Description pour {title}..."

                entry = {
                    "id": f"{cat}_{basename}",
                    "category": cat,
                    "src": img_path,
                    "title": title,
                    "year": year,
                    "description": description
                }
                catalog.append(entry)
                
    # On génère un fichier JS au lieu d'un JSON pour éviter les erreurs CORS en local
    js_content = f"const GALLERY_DATA = {json.dumps(catalog, indent=2, ensure_ascii=False)};"
    with open('js/data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
        
    print(f"✅ Synchronisation terminée. {len(catalog)} photos trouvées et encodées dans js/data.js")

if __name__ == "__main__":
    generate_catalog()
