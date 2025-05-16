import os
import shutil
from tkinter import Tk, filedialog

# 啟用 GUI 選擇視窗
def select_folder(prompt_title):
    root = Tk()
    root.withdraw()  # 不顯示主視窗
    folder_selected = filedialog.askdirectory(title=prompt_title)
    root.destroy()
    return folder_selected

# 讓使用者輸入想篩選的關鍵字
keywords = input("請輸入篩選檔案的關鍵字（名字要完全一樣例如：sensor1），多個關鍵字請以逗號分隔：").split(',')

# 去除每個關鍵字前後的空白字元
keywords = [keyword.strip() for keyword in keywords]

# 選擇來源資料夾
source_folder = select_folder("請選擇原始資料夾")

# 選擇目標資料夾
target_folder = select_folder("請選擇目標資料夾")

# 建立目標資料夾（如果不存在）
os.makedirs(target_folder, exist_ok=True)

# 遍歷來源資料夾內所有檔案，篩選出符合條件的 .tsv 檔案
for filename in os.listdir(source_folder):
    if filename.endswith('.tsv'):  # 只處理 .tsv 檔案
        # 檢查檔名中是否包含任何一個關鍵字
        if any(keyword in filename for keyword in keywords):
            src_path = os.path.join(source_folder, filename)
            dst_path = os.path.join(target_folder, filename)
            shutil.copy2(src_path, dst_path)  # 若要移動檔案，可改成 shutil.move

print("檔案收集完成！")
