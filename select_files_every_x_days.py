import os
import shutil
from datetime import datetime
from tkinter import Tk, filedialog

# 開啟選擇資料夾視窗
def select_folder(prompt):
    root = Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title=prompt)
    return folder

# 1️⃣ 選擇來源資料夾
source_folder = select_folder("請選擇來源資料夾")
if not source_folder:
    print("未選擇來源資料夾，結束。")
    exit()

# 2️⃣ 選擇目標資料夾
target_folder = select_folder("請選擇要儲存檔案的新資料夾")
if not target_folder:
    print("未選擇目標資料夾，結束。")
    exit()

# 建立目標資料夾（如不存在）
os.makedirs(target_folder, exist_ok=True)

# 3️⃣ 收集符合條件的檔案（含日期）
date_file_map = {}

for filename in os.listdir(source_folder):
    parts = filename.split("_")
    if len(parts) >= 5:
        try:
            date_str = f"{parts[2]}_{parts[3]}_{parts[4]}"
            date_obj = datetime.strptime(date_str, "%Y_%m_%d")
            date_file_map[date_obj] = filename
        except ValueError:
            continue  # 無法解析日期的檔名略過

# 4️⃣ 排序日期、保留每兩天一個檔案
sorted_dates = sorted(date_file_map.keys())
selected_files = []
last_date = None

for date in sorted_dates:
    if last_date is None or (date - last_date).days >= 2:
        selected_files.append(date_file_map[date])
        last_date = date

# 5️⃣ 複製檔案到新資料夾
for file in selected_files:
    src_path = os.path.join(source_folder, file)
    dst_path = os.path.join(target_folder, file)
    shutil.copy2(src_path, dst_path)

# ✅ 完成訊息
print("已複製以下檔案至目標資料夾：")
for f in selected_files:
    print(f"✔ {f}")
