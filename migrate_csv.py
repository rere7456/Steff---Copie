import os
import csv
import re

TXT_FILE = 'data/descriptions.txt'
CSV_FILE = 'data/database.csv'

def migrate_to_csv():
    # 1. Lire l'ancien fichier texte
    if not os.path.exists(TXT_FILE):
        print("Pas de fichier descriptions.txt trouvé.")
        return

    with open(TXT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 2. Parser les données
    entries = []
    # Regex pour capturer [fichier], Date: ..., Description: ...
    pattern = re.compile(r'\[(.*?)\]\s+Date:\s*(.*?)\s+Description:\s*(.*?)(?=\n\[|$)', re.DOTALL)
    
    matches = pattern.findall(content)
    
    for filename, date, desc in matches:
        # Nettoyage
        filename = filename.strip()
        date = date.strip()
        desc = desc.strip()
        
        # On déduit un titre propre depuis le nom du fichier
        title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()
        title = title.replace("'", "•").replace("é", "e").replace("É", "E")
        
        entries.append([filename, title, date, desc])

    # 3. Écrire le fichier CSV (Compatible Excel : point-virgule comme séparateur)
    with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f: # utf-8-sig pour qu'Excel reconnaisse les accents
        writer = csv.writer(f, delimiter=';')
        # En-têtes
        writer.writerow(['Nom_Fichier_Image', 'Titre', 'Annee', 'Description'])
        writer.writerows(entries)

    print(f"✅ Migration terminée ! Vous pouvez maintenant ouvrir {CSV_FILE} avec Excel.")

if __name__ == "__main__":
    migrate_to_csv()
