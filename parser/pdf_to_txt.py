import os
import fitz  # PyMuPDF

# Set your folder path
pdf_folder = "./Books"
output_folder = os.path.join(pdf_folder, "txt")

print("📁 Creating output folder (if it doesn't exist)...")
os.makedirs(output_folder, exist_ok=True)
print(f"✅ Output folder is set: {output_folder}\n")

# List all files in the folder
files = os.listdir(pdf_folder)
print(f"🔍 Found {len(files)} files in folder.\n")

for filename in files:
    print(f"--- Checking: {filename}")
    if not filename.lower().endswith(".pdf") or filename.startswith("."):
        print("⏭️ Skipping (not a PDF or hidden file)\n")
        continue

    pdf_path = os.path.join(pdf_folder, filename)
    base_name = os.path.splitext(filename)[0]

    try:
        print(f"📄 Opening PDF: {filename}")
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        print(f"📑 Pages in PDF: {total_pages}")

        for page_num in range(total_pages):
            page = doc.load_page(page_num)
            text = page.get_text()

            txt_filename = f"{base_name}_page_{page_num + 1}.txt"
            txt_path = os.path.join(output_folder, txt_filename)

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)

            print(f"✅ Wrote: {txt_filename}")

        doc.close()
        print(f"🎉 Done with: {filename}\n")

    except Exception as e:
        print(f"❌ Error with {filename}: {e}\n")

print("✅ All done!")
