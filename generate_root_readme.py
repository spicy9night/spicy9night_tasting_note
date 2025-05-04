import os
import re
from PIL import Image
import piexif

def generate_toc(root_dir=".", level=0):
    toc = ""
    items = sorted(os.listdir(root_dir))
    for item in items:
        full_path = os.path.join(root_dir, item)

        # 忽略以 . 開頭的資料夾（例如 .git, .vscode）
        if item.startswith(".") or item.startswith("Tool") or item.startswith("todo") :
            continue

        readme_path = os.path.join(full_path, "README.md")
        
        if os.path.isdir(full_path):
            # 確認資料夾裡是否只有 README.md
            has_readme = os.path.isfile(readme_path)
            contains_other_files = any(os.path.isdir(os.path.join(full_path, sub_item)) for sub_item in os.listdir(full_path))
            indent = "&nbsp;" * (level * 2)

            if has_readme and not contains_other_files:
                # 只有 README.md 的資料夾，直接顯示連結，不使用 details 和 summary
                folder_emoji = "📄"  # 使用筆記 emoji
                toc += f'{indent}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="{readme_path}">{folder_emoji} {item}</a>\n\n'
            else:
                # 有子資料夾或其他檔案的資料夾，使用摺疊式顯示
                folder_emoji = "📁" if level == 0 else "📂"  # 根據層級顯示不同 emoji
                toc += f'<details>\n'
                toc += f'<summary>{indent}<a href="{readme_path}">{folder_emoji} {item}</a></summary>\n\n'
                
                # 遞迴生成子資料夾的目錄
                toc += generate_toc(full_path, level + 1)
                toc += f'</details>\n\n'

    return toc

def replace_menu_section(readme_path, toc_md):
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    new_menu_block = f"# Menu\n\n{toc_md.strip()}\n"

    new_content = re.sub(
        r"# Menu\n(.*?)(?=\n#|\Z)",
        lambda m: new_menu_block,
        content,
        flags=re.DOTALL
    )

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"✅ 已更新 {readme_path} 中的 # Menu 區塊")

def remove_gps_and_overwrite(image_path):
    try:
        img = Image.open(image_path)
        if "exif" in img.info:
            exif_dict = piexif.load(img.info["exif"])
            exif_dict["GPS"] = {}  # 移除 GPS 資訊
            exif_bytes = piexif.dump(exif_dict)
            img.save(image_path, "jpeg", exif=exif_bytes)
            print(f"✅ 已移除 GPS：{image_path}")
        else:
            print(f"⚠️ 無 EXIF 資訊，略過：{image_path}")
    except Exception as e:
        print(f"❌ 錯誤處理 {image_path}：{e}")

def process_folder_recursively(root_folder):
    for dirpath, dirnames, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.lower().endswith((".jpg", ".jpeg")):
                full_path = os.path.join(dirpath, filename)
                remove_gps_and_overwrite(full_path)


if __name__ == "__main__":
    toc = generate_toc(".")
    replace_menu_section("README.md", toc)
    
    folder_path = "."
    process_folder_recursively(folder_path)
