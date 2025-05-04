X
import fitz  # PyMuPDF
import os

def pdf_to_jpg_no_poppler(pdf_path, output_folder, dpi=600):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    doc = fitz.open(pdf_path)
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        pix = page.get_pixmap(dpi=dpi)

        output_path = os.path.join(output_folder, f"page_{page_number + 1}.jpg")
        pix.save(output_path)
        print(f"✅ 儲存：{output_path}")

    print("🎉 所有頁面已轉換完成")

# 使用方式
pdf_path = "1.pdf"
output_folder = "output"
pdf_to_jpg_no_poppler(pdf_path, output_folder, dpi=600)