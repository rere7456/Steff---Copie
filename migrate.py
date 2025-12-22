import os

CATEGORIES = ['mariages', 'nature-paysages', 'portrait-reportages', 'urbain', 'creatif']
database_path = "data/descriptions.txt"

existing_data = ""

for cat in CATEGORIES:
    data_dir = os.path.join('data', cat)
    if not os.path.exists(data_dir):
        continue
        
    files = os.listdir(data_dir)
    for filename in files:
        if filename.endswith(".txt"):
            # On trouve le nom de l'image correspondante (on suppose jpg pour la migration, mais le sync corrigera)
            img_name = filename.replace(".txt", ".jpg") 
            
            file_path = os.path.join(data_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parsing simple pour récupérer ce qu'il y a dedans
            date = ""
            desc = ""
            for line in content.splitlines():
                if "date :" in line.lower():
                    date = line.split(":", 1)[1].strip()
                if "description :" in line.lower() or "descritpion :" in line.lower():
                    desc = line.split(":", 1)[1].strip()
            
            # Ajout au fichier global
            # On essaie de retrouver le vrai nom de l'image dans le dossier images si possible
            real_img_name = img_name
            img_dir = os.path.join('images', cat)
            if os.path.exists(img_dir):
                for f in os.listdir(img_dir):
                    if os.path.splitext(f)[0] == os.path.splitext(filename)[0]:
                        real_img_name = f
                        break

            existing_data += f"[{real_img_name}]\n"
            existing_data += f"Date: {date}\n"
            existing_data += f"Description: {desc}\n"
            existing_data += "\n"

# Écriture du fichier unique
with open(database_path, 'w', encoding='utf-8') as f:
    f.write(existing_data)

print(f"Migration terminée : {database_path} créé.")
