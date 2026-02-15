import os
import re
from PIL import Image
import piexif
import datetime

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

def has_exif(file_path):
    """檢查照片是否有 EXIF 資料"""
    try:
        exif_dict = piexif.load(file_path)
        # 檢查是否有任何 EXIF 資料
        for ifd in exif_dict.values():
            if ifd:
                return True
        return False
    except:
        return False

def remove_exif_from_image(file_path):
    try:
        if not has_exif(file_path):
            # print(f"⏭️ 跳過（無EXIF）: {file_path}")
            return
        piexif.remove(file_path)
        print(f"✅ 已移除 EXIF: {file_path}")
    except Exception as e:
        print(f"❌ 處理失敗 {file_path}: {e}")

def get_tasting_info(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.split('\n')
    title = ""
    tasting_date = None
    for line in lines:
        if line.startswith('# '):
            title = line.strip('# ').strip()
            break
    flavor_parts = []
    for line in lines:
        if '### 【日期】' in line:
            tasting_date = line.split('### 【日期】')[1].strip()
        elif '### 【香氣】' in line:
            flavor_parts.append(line.split('### 【香氣】')[1].strip())
        elif '### 【味道】' in line:
            flavor_parts.append(line.split('### 【味道】')[1].strip())
        elif '### 【結語】' in line:
            flavor_parts.append(line.split('### 【結語】')[1].strip())
    flavor_summary = ' '.join(flavor_parts)
    return title, tasting_date, flavor_summary

def parse_table(content):
    lines = content.split('\n')
    entries = []
    in_table = False
    for line in lines:
        if '| 新增日期' in line:
            in_table = True
            continue
        if in_table and line.startswith('|') and '|' in line and not '---' in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 6 and parts[1] != '新增日期':
                entry = {
                    'add_date': parts[1],
                    'tasting_date': parts[2],
                    'name': parts[3],
                    'flavor': parts[4],
                    'link': parts[5]
                }
                entries.append(entry)
        if line.startswith('<details>'):
            break
    # Show All
    in_show_all = False
    for line in lines:
        if '<summary>Show All</summary>' in line:
            in_show_all = True
            continue
        if in_show_all and line.startswith('|') and '|' in line and not '---' in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 6 and parts[1] != '新增日期':
                entry = {
                    'add_date': parts[1],
                    'tasting_date': parts[2],
                    'name': parts[3],
                    'flavor': parts[4],
                    'link': parts[5]
                }
                entries.append(entry)
    return entries

def process_folder_recursively(root_folder):
    for dirpath, dirnames, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.lower().endswith((".jpg", ".jpeg")):
                full_path = os.path.join(dirpath, filename)
                remove_exif_from_image(full_path)


if __name__ == "__main__":
    current_date = datetime.date.today().strftime('%Y.%m.%d')
    
    # Find all README.md files
    readme_files = []
    for root, dirs, files in os.walk('.'):
        if 'README.md' in files and root != '.':
            readme_files.append(os.path.join(root, 'README.md'))
    
    # Read root README
    with open('README.md', 'r', encoding='utf-8') as f:
        root_content = f.read()
    
    # Parse existing entries
    existing_entries = parse_table(root_content)
    
    # Get existing links
    existing_links = {re.sub(r'^\[Note\]\((.*)\)$', r'\1', e['link']) for e in existing_entries}
    # print("Existing links:")
    # for link in sorted(existing_links):
    #     print(f"  {link}")
    
    # Find new entries
    confirmed_new_entries = []
    for readme in readme_files:
        rel_path = './' + os.path.relpath(readme).replace('\\', '/')
        # print(f"Checking {readme}: rel_path = {rel_path}, in existing_links = {rel_path in existing_links}")
        if rel_path not in existing_links:
            title, tasting_date, flavor = get_tasting_info(readme)
            if tasting_date:
                print(f"\nNew tasting note detected: {title}")
                print(f"Tasting date: {tasting_date}")
                print(f"Flavor summary: {flavor}")
                print(f"Path: {rel_path}")
                print("Reason: This README.md file was not found in the current history table.")
                confirm = input("Add this to the update history? (y/n, default: y): ").strip().lower() or 'y'
                if confirm == 'y':
                    entry = {
                        'add_date': current_date,
                        'tasting_date': tasting_date,
                        'name': title,
                        'flavor': flavor,
                        'link': f'[Note]({rel_path})'
                    }
                    confirmed_new_entries.append(entry)
    
    # All entries
    all_entries = existing_entries + confirmed_new_entries
    
    # Sort by add_date desc
    all_entries.sort(key=lambda e: datetime.datetime.strptime(e['add_date'], '%Y.%m.%d'), reverse=True)
    
    # Top 3 for main, rest for show all
    main_entries = all_entries[:3]
    show_all_entries = all_entries[3:]
    
    # Format the history section
    header = """# update history
| 新增日期   | 品飲日期    | 酒 款                                              | 風味概述                        | 筆記      |
|------------|-------------|----------------------------------------------------|---------------------------------|-----------|"""
    
    main_table = '\n'.join([f"| {e['add_date']} | {e['tasting_date']}  | {e['name']} | {e['flavor']} | {e['link']} |" for e in main_entries])
    
    if show_all_entries:
        show_all_table = '\n'.join([f"| {e['add_date']} | {e['tasting_date']}  | {e['name']} | {e['flavor']} | {e['link']} |" for e in show_all_entries])
        show_all_section = f"""
    
<details>
<summary>Show All</summary>

| 新增日期    | 品飲日期    | 酒 款                                | 風味概述                        | 筆記      |
|-------------|-------------|--------------------------------------|---------------------------------|-----------|
{show_all_table}
</details>"""
    else:
        show_all_section = ""
    
    new_history_section = f"{header}\n{main_table}{show_all_section}\n\n"
    
    # Replace in root_content
    pattern = r"(# update history\n.*?)(?=\n#|\Z)"
    root_content = re.sub(pattern, new_history_section, root_content, flags=re.DOTALL)
    
    # Write back
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(root_content)
    
    print("✅ 已更新 Update History 區塊")
    
    toc = generate_toc(".")
    replace_menu_section("README.md", toc)
    
    folder_path = "."
    process_folder_recursively(folder_path)
