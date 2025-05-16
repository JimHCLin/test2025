import os
import shutil
from datetime import datetime
from tkinter import Tk, filedialog, simpledialog, messagebox

def select_folder(prompt):
    root = Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title=prompt)
    return folder

def ask_interval_days():
    root = Tk()
    root.withdraw()
    days = simpledialog.askinteger("間隔設定", "請輸入每隔幾天保留一個檔案：", minvalue=1)
    return days

def filter_files_by_date_interval(source_folder, target_folder, interval_days=2):
    date_file_map = {}

    for filename in os.listdir(source_folder):
        parts = filename.split("_")
        if len(parts) >= 5:
            try:
                date_str = f"{parts[2]}_{parts[3]}_{parts[4]}"
                date_obj = datetime.strptime(date_str, "%Y_%m_%d")
                date_file_map[date_obj] = filename
            except ValueError:
                continue

    sorted_dates = sorted(date_file_map.keys())
    selected_files = []
    last_date = None

    for date in sorted_dates:
        if last_date is None or (date - last_date).days >= interval_days:
            selected_files.append(date_file_map[date])
            last_date = date

    os.makedirs(target_folder, exist_ok=True)

    for file in selected_files:
        src_path = os.path.join(source_folder, file)
        dst_path = os.path.join(target_folder, file)
        shutil.copy2(src_path, dst_path)

    print(f"✅ 已複製 {len(selected_files)} 個檔案至：{target_folder}")
    for f in selected_files:
        print(f"✔ {f}")

    # 顯示完成視窗
    messagebox.showinfo("完成", f"已成功複製 {len(selected_files)} 個檔案至指定資料夾！")

# 主程式
if __name__ == "__main__":
    source = select_folder("請選擇來源資料夾")
    if not source:
        print("❌ 未選擇來源資料夾，結束。")
        exit()

    target = select_folder("請選擇儲存篩選檔案的新資料夾")
    if not target:
        print("❌ 未選擇目標資料夾，結束。")
        exit()

    interval = ask_interval_days()
    if interval is None:
        print("❌ 未輸入間隔天數，結束。")
        exit()

    filter_files_by_date_interval(source, target, interval_days=interval)
