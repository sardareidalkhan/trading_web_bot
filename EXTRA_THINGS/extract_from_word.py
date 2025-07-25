# extract_from_word.py
# ✅ This script will extract all screenshots from UP.docx and DOWN.docx
#    exactly how they are used during ML training — same resolution, same format

import os
from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml.ns import qn
from docx.oxml import parse_xml
import shutil

# === CONFIG ===
DOCX_PATHS = {
    "UP": "dataset/UP.docx",
    "DOWN": "dataset/DOWN.docx",
}
OUTPUT_FOLDER = "extracted_screens"

# === Prepare output folders ===
if os.path.exists(OUTPUT_FOLDER):
    shutil.rmtree(OUTPUT_FOLDER)
os.makedirs(OUTPUT_FOLDER)

for label, docx_path in DOCX_PATHS.items():
    print(f"📂 Extracting from: {docx_path}")
    try:
        doc = Document(docx_path)
        rels = doc.part.rels
        count = 0

        for rel in rels:
            rel_obj = rels[rel]
            if rel_obj.reltype == RT.IMAGE:
                count += 1
                image_data = rel_obj.target_part.blob

                save_folder = os.path.join(OUTPUT_FOLDER, label)
                os.makedirs(save_folder, exist_ok=True)
                
                with open(os.path.join(save_folder, f"{label}_{count}.png"), 'wb') as f:
                    f.write(image_data)

        print(f"✅ {count} images saved to: {save_folder}\n")

    except Exception as e:
        print(f"❌ Error extracting from {docx_path}: {e}")

print("✅ All done. Check the extracted_screens/ folder.")
