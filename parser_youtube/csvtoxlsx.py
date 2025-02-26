import pandas as pd
import os

CSV_FILE = "youtube_channels.csv"
EXCEL_FILE = "youtube_channels.xlsx"

if not os.path.exists(CSV_FILE):
    print(f"Файл {CSV_FILE} не найден!")
    exit()

try:
    df = pd.read_csv(CSV_FILE)
except Exception as e:
    print(f"Ошибка при чтении CSV: {e}")
    exit()

with pd.ExcelWriter(EXCEL_FILE, engine="xlsxwriter") as writer:
    df.to_excel(writer, sheet_name="YouTube Channels", index=False)

    workbook = writer.book
    worksheet = writer.sheets["YouTube Channels"]
    for i, col in enumerate(df.columns):
        max_len = max(df[col].astype(str).apply(len).max(), len(col)) + 2
        worksheet.set_column(i, i, max_len)

print(f"Файл сохранен: {EXCEL_FILE}")
