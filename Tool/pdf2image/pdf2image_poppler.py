from pdf2image import convert_from_path
import os

def pdf_to_jpg(pdf_path, output_folder, dpi=200, poppler_path=None):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    print("📄 轉換中...")

    # 轉換 PDF 成圖像列表
    images = convert_from_path(pdf_path, dpi=dpi, poppler_path=poppler_path)

    for i, image in enumerate(images):
        output_path = os.path.join(output_folder, f"ppage_{i+1}.jpg")
        image.save(output_path, "JPEG")
        print(f"✅ 已儲存：{output_path}")

    print("🎉 轉換完成！")

# 使用方式
pdf_path = "1.pdf"
output_folder = "output"
poppler_path = r".\poppler-24.08.0\Library\bin"  # Windows 用戶需填入 Poppler bin 路徑，Linux/macOS 可設為 None


pdf_to_jpg(pdf_path, output_folder, dpi=200, poppler_path=poppler_path)