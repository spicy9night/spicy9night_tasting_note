import os
import shutil
import hashlib
from pathlib import Path
from typing import Dict, Set


def calculate_file_hash(file_path: str) -> str:
    """計算檔案的 SHA256 雜湊值"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_file_hashes(folder_path: str) -> Dict[str, str]:
    """取得資料夾中所有檔案的雜湊值對應"""
    file_hashes = {}
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"❌ 資料夾不存在: {folder_path}")
        return file_hashes
    
    for file_path in folder.rglob("*"):
        if file_path.is_file():
            try:
                file_hash = calculate_file_hash(str(file_path))
                file_hashes[file_hash] = str(file_path)
            except Exception as e:
                print(f"⚠️  無法讀取檔案 {file_path}: {e}")
    
    return file_hashes


def compare_and_move_files(folder_a: str, folder_b: str, folder_c: str = None) -> None:
    """
    比較資料夾 A 和 B，將 B 中與 A 相同的檔案移到 C 資料夾
    
    Args:
        folder_a: 資料夾 A 的路徑
        folder_b: 資料夾 B 的路徑
        folder_c: 資料夾 C 的路徑（若為 None 則自動在 B 的同層目錄建立）
    """
    
    # 驗證輸入
    folder_a = os.path.abspath(folder_a)
    folder_b = os.path.abspath(folder_b)
    
    if not os.path.isdir(folder_a):
        print(f"❌ 資料夾 A 不存在: {folder_a}")
        return
    
    if not os.path.isdir(folder_b):
        print(f"❌ 資料夾 B 不存在: {folder_b}")
        return
    
    # 自動建立資料夾 C（若未指定）
    if folder_c is None:
        parent_dir = os.path.dirname(folder_b)
        folder_c = os.path.join(parent_dir, "C_duplicates")
    
    folder_c = os.path.abspath(folder_c)
    
    # 建立資料夾 C
    try:
        Path(folder_c).mkdir(parents=True, exist_ok=True)
        print(f"✓ 資料夾 C 已建立: {folder_c}\n")
    except Exception as e:
        print(f"❌ 無法建立資料夾 C: {e}")
        return
    
    # 計算 A 和 B 的文件雜湊值
    print("📊 計算資料夾 A 的文件雜湊值...")
    hashes_a = get_file_hashes(folder_a)
    print(f"   找到 {len(hashes_a)} 個檔案\n")
    
    print("📊 計算資料夾 B 的文件雜湊值...")
    hashes_b = get_file_hashes(folder_b)
    print(f"   找到 {len(hashes_b)} 個檔案\n")
    
    # 找出重複的檔案
    hashes_a_set = set(hashes_a.keys())
    duplicate_hashes = hashes_a_set & set(hashes_b.keys())
    
    if not duplicate_hashes:
        print("✓ 沒有找到重複的檔案")
        return
    
    print(f"🔍 找到 {len(duplicate_hashes)} 個重複的檔案\n")
    
    # 移動重複的檔案
    moved_count = 0
    failed_count = 0
    
    for file_hash in duplicate_hashes:
        file_b_path = hashes_b[file_hash]
        file_name = os.path.basename(file_b_path)
        dest_path = os.path.join(folder_c, file_name)
        
        # 處理檔案名稱重複的情況
        counter = 1
        while os.path.exists(dest_path):
            name_parts = file_name.rsplit(".", 1)
            if len(name_parts) == 2:
                dest_path = os.path.join(folder_c, f"{name_parts[0]}_{counter}.{name_parts[1]}")
            else:
                dest_path = os.path.join(folder_c, f"{file_name}_{counter}")
            counter += 1
        
        try:
            shutil.move(file_b_path, dest_path)
            print(f"✓ 已移動: {file_name} → {folder_c}")
            moved_count += 1
        except Exception as e:
            print(f"❌ 移動失敗: {file_name} - {e}")
            failed_count += 1
    
    print(f"\n📈 完成")
    print(f"   成功移動: {moved_count} 個檔案")
    if failed_count > 0:
        print(f"   移動失敗: {failed_count} 個檔案")


def main():
    """主程式"""
    print("=" * 60)
    print("檔案比較與移動工具")
    print("=" * 60 + "\n")
    
    # 獲取使用者輸入
    folder_a = input("請輸入資料夾 A 的路徑: ").strip()
    if not folder_a:
        print("❌ 不能為空")
        return
    
    folder_b = input("請輸入資料夾 B 的路徑: ").strip()
    if not folder_b:
        print("❌ 不能為空")
        return
    
    folder_c_input = input("請輸入資料夾 C 的路徑 (留空則自動建立): ").strip()
    folder_c = folder_c_input if folder_c_input else None
    
    print("\n" + "=" * 60 + "\n")
    
    compare_and_move_files(folder_a, folder_b, folder_c)


if __name__ == "__main__":
    main()
