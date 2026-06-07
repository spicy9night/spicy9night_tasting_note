import os
import sys
import subprocess
from pathlib import Path

PROMPT_FILE = Path(__file__).with_name("prompt.md")
OUTPUT_FILE = Path(__file__).with_name("prompt_for_vscode_chat.txt")

FIELDS = [
    "Distillery",
    "Vintage",
    "Stated Age",
    "Cask Type",
    "Strength",
    "Points",
    "Price",
    "Category",
    "OB/Bottler",
    "Bottling series",
    "# bottles",
    "Tasting Note",
    "Link",
    "Folder Name",
    "Title",
]

HEADER_LINE = "\t".join(FIELDS)


def read_prompt_template() -> str:
    if PROMPT_FILE.is_file():
        return PROMPT_FILE.read_text(encoding="utf-8")
    return """你現在是一個懂得「spicy9night_tasting_note」專案文章格式的寫手。我會給你一筆品酒的 row data，請你幫我生成一篇完整的 README.md 文章，格式要符合專案現有筆記風格。

要求：
1. 在 `Distillery` 資料夾底下建立 `Folder Name` 資料夾，並新增 `README.md` 在裡面。
2. README.md 必要格式如下：
   - 第一行用 `# `，標題使用 `Title`，如果沒有 `Title` 就用 `Distillery + Vintage + Stated Age + Cask Type + Strength` 組成。
   - 內容至少要有：
     - `### 【香氣】`
     - `### 【味道】`
     - `### 【結語】`
     - `### 【日期】` 當天日期，例如 `2026.5.18`
     - `### 【評分】` 對應 `points`
     - `### 【價格】` 對應 `price`
3. 文章文字要用中文，風格自然、品酒日記型、貼近專案現有 README 內容。
4. 如果欄位有 `Category`、`OB/Bottler`、`Bottling series`、`Cask Type`、`Strength`，請適度融入描述背景與酒款特色。
5. 結尾可加簡單 hashtag，例如 `#whisky #spicy9night`。
6. hashtag 規則：
   - 固定標籤：`#whisky #whiskylover #whiskey #spicy9night`
   - 如果 `Distillery` 有值，請加上對應的 distillery hashtag，例如 `#bowmore`、`#glenfiddich`。
   - 如果 `OB/Bottler` 有值，請加上對應的裝瓶廠 hashtag，例如 `#signatoryvintage`。
   - 只有當 `OB/Bottler` 是 `whiskyfind` 時，才加上 `#whiskyfind`。
   - 不要把 `#bowmore` 或任何酒廠 hashtag 當成固定標籤，應該根據 `Distillery` 欄位決定。
7. 最後直接輸出完整 README.md 內容，不要輸出表格或 JSON。
8. 如果 `price` 欄位為空，也要保留 `### 【價格】` 標題，但內容可以留空。
9. 最尾巴加上picture 的MD 
   - ![picture](./1.jpg)
   - ![picture](./2.jpg)
   - ![picture](./3.jpg)
   - ![picture](./12.jpeg)

下面是我給你的 row data，請依此產出文章並直接新增 `README.md`：

"""


def prompt_user_for_value(prompt_text: str, required: bool = False) -> str:
    while True:
        value = input(prompt_text).strip()
        if value or not required:
            return value
        print("此欄位不可為空，請重新輸入。")


def prompt_multiline(prompt_text: str) -> str:
    print(prompt_text)
    print("輸入多行文字，完成後按 Enter 兩次結束。")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "":
            if lines:
                break
            continue
        lines.append(line)
    return "\n".join(lines)


def parse_raw_row(raw_row: str) -> dict:
    parts = raw_row.strip().split("\t")
    if len(parts) != len(FIELDS):
        raise ValueError(
            f"Raw data 欄位數量不正確，請輸入 {len(FIELDS)} 個欄位，用 Tab 分隔。"
        )
    return dict(zip(FIELDS, parts))


def build_row_text(values: dict) -> str:
    row = []
    for field in FIELDS:
        value = values.get(field, "")
        if field == "Tasting Note" and "\n" in value:
            # preserve newlines inside a quoted field
            row.append(f'"{value}"')
        else:
            row.append(value)
    return HEADER_LINE + "\n" + "\t".join(row)


def copy_to_clipboard(text: str) -> bool:
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception:
        pass

    if os.name == "nt":
        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", "Set-Clipboard -Value $input"],
                input=text,
                text=True,
                check=True,
            )
            return True
        except Exception:
            return False

    if sys.platform == "darwin":
        try:
            proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
            proc.communicate(input=text.encode("utf-8"))
            return proc.returncode == 0
        except Exception:
            return False

    try:
        proc = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
        proc.communicate(input=text.encode("utf-8"))
        return proc.returncode == 0
    except Exception:
        return False


def main() -> None:
    print("=== add_tasting_note.py ===")
    print("這個腳本會根據 prompt.md 範本，生成可貼到 VS Code Chat 的 prompt。\n")

    prompt_template = read_prompt_template()
    if not prompt_template:
        print("找不到 prompt.md，將使用內建範本。\n")

    use_raw = input("是否要直接貼入 raw data 行內容？(y/n, 預設 n): ").strip().lower() == "y"
    values = {}

    if use_raw:
        raw_row = input("請貼入 raw data 行，Tab 分隔欄位: ").strip()
        if not raw_row:
            print("沒有輸入內容。改成互動式填寫。\n")
        else:
            try:
                values = parse_raw_row(raw_row)
            except ValueError as exc:
                print(f"錯誤: {exc}\n將改成互動式填寫。")
                values = {}

    if not values:
        print("請根據以下欄位依序輸入資料：")
        for field in FIELDS:
            if field == "Tasting Note":
                value = prompt_multiline(f"{field}: ")
            else:
                value = prompt_user_for_value(f"{field}: ")
            values[field] = value

    row_text = build_row_text(values)
    final_prompt = prompt_template.strip() + "\n\n" + row_text + "\n"

    OUTPUT_FILE.write_text(final_prompt, encoding="utf-8")

    print("\n--- 已產生 prompt，已寫入: {}".format(OUTPUT_FILE))
    print("請將以下內容貼到 VS Code Chat 中，或開啟生成的檔案進行複製。\n")
    print(final_prompt)

    if copy_to_clipboard(final_prompt):
        print("\n已將 prompt 複製到剪貼簿。可直接貼到 VS Code Chat。")
    else:
        print("\n無法複製到剪貼簿。請手動複製上方輸出內容。\n")


if __name__ == "__main__":
    main()
