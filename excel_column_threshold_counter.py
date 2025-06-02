import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import pandas as pd
from openpyxl import load_workbook
import os

def select_file_and_process():
    # 選擇 Excel 檔案
    filepath = filedialog.askopenfilename(
        title="選擇 Excel 檔案", 
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    if not filepath:
        return

    # 輸入閥值
    try:
        threshold = simpledialog.askfloat("輸入閥值", "請輸入數值作為閥值：")
        if threshold is None:
            return
    except ValueError:
        messagebox.showerror("輸入錯誤", "請輸入有效的數值")
        return

    # 讀取 Excel
    try:
        df = pd.read_excel(filepath, engine="openpyxl")
        
        print("欄位名稱:", df.columns.tolist())
    except Exception as e:
        messagebox.showerror("錯誤", f"讀取 Excel 時發生錯誤：\n{e}")
        return

    # 要處理的欄位
    target_columns = [
    'Top1_頻率_Hz',
    'Top2_頻率_Hz',
    'Top3_頻率_Hz',
    'Top4_頻率_Hz',
    'Top5_頻率_Hz'
]
    results = {}
    over_values = {}

    for col in target_columns:
        if col in df.columns:
            #col_values = df[col].iloc[0:].dropna()
            col_values = pd.to_numeric(df[col], errors='coerce').dropna()
            over = col_values[col_values > threshold]
            results[col] = int(len(over))
            over_values[col] = list(over.values)
            #print(f"over_values:{over_values}")
        else:
            results[col] = "欄位不存在"
            over_values[col] = []

    # 顯示統計 + 數值預覽訊息框
    preview_lines = []
    for col in target_columns:
        values = over_values.get(col, [])
        preview = ', '.join(map(str, values[:10])) if values else "無資料"
        preview_lines.append(f"{col} 欄位 > {threshold} 的筆數：{results[col]}\n→ 前幾筆數值：{preview}")
    messagebox.showinfo("統計結果（含數值預覽）", "\n\n".join(preview_lines))

    # 寫入 Excel 的兩個工作表
    try:
        # 統計結果 DataFrame
        result_df = pd.DataFrame([
            {
                "欄位": col,
                f"大於 {threshold} 的筆數": results[col]
            } for col in target_columns
        ])

        # 詳細數值 DataFrame（長格式）
        detail_data = []
        for col in target_columns:
            for value in over_values[col]:
                detail_data.append({"欄位": col, "數值": value})
        detail_df = pd.DataFrame(detail_data)

        # 用 openpyxl 寫入原 Excel（新增或覆蓋工作表）
        #book = load_workbook(filepath)
        ###
        '''
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="另存新檔"
        )
        with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
            result_df.to_excel(writer, sheet_name='統計結果', index=False)
            detail_df.to_excel(writer, sheet_name='超過閥值明細', index=False)
            '''
                ###
       # with pd.ExcelWriter(filepath, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        #    writer.book = book
         #   result_df.to_excel(writer, sheet_name='統計結果', index=False)
          #  detail_df.to_excel(writer, sheet_name='超過閥值明細', index=False)

        ###
                
        output_filename = f"ThresholdValue_{threshold}_counter.xlsx"
        output_path = os.path.join(os.path.dirname(filepath), output_filename)

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            result_df.to_excel(writer, sheet_name='統計結果', index=False)
            detail_df.to_excel(writer, sheet_name='超過閥值明細', index=False)

        messagebox.showinfo("儲存完成", f"結果已儲存為：\n{output_path}")
        #messagebox.showinfo("儲存完成", f"統計與數值明細已寫入：\n{filepath}")
    except Exception as e:
        messagebox.showerror("儲存錯誤", f"無法寫入 Excel：\n{e}")

# 執行程式
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    select_file_and_process()
