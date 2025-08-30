# convert_xlsx_to_json.py
import os, json
import pandas as pd

EXCEL_FILES = {
    "2021": "results_2021.xlsx",
    "2022": "results_2022.xlsx",
    "2023": "results_2023.xlsx",
    "2024": "results_2024.xlsx",
    "2025": "results_2025.xlsx"
}

def find_col(df, candidates):
    for col in df.columns:
        for c in candidates:
            if c.lower() in str(col).lower():
                return col
    return None

NUMBER_COLS = ["Number","number","رقم_الجلوس","رقم","roll","seat","id","ID"]
NAME_COLS   = ["الاسم","اسم","name","Name","الطالب"]

all_records = []

for year, fname in EXCEL_FILES.items():
    if not os.path.exists(fname):
        print(f"⚠️ ملف غير موجود: {fname} — يتخطى {year}")
        continue
    df = pd.read_excel(fname, dtype=str).fillna("")
    num_col = find_col(df, NUMBER_COLS) or df.columns[0]
    name_col = find_col(df, NAME_COLS) or (df.columns[1] if len(df.columns)>1 else df.columns[0])
    df[num_col] = df[num_col].astype(str).str.strip()
    for _, row in df.iterrows():
        rec = {"year": year, "number": row.get(num_col, ""), "name": row.get(name_col, "")}
        # أحفظ كل الأعمدة الأخرى داخل dict
        extras = {}
        for col in df.columns:
            if col not in [num_col, name_col]:
                extras[str(col)] = row.get(col, "")
        rec["fields"] = extras
        all_records.append(rec)

out = {"count": len(all_records), "results": all_records}
with open("results.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print("✅ تم إنشاء results.json — السجلات:", len(all_records))
