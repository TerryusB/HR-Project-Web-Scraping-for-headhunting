import os
import re
import pandas as pd

# 1) Detecta la carpeta del script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2) Archivo maestro con tus hojas DATASET 0 y Listas
FNAME = os.path.join(BASE_DIR, "Proyecto Análisis de perfiles para gerencia .xlsx")

# 3) Carga hojas
df     = pd.read_excel(FNAME, sheet_name="DATASET 0")
listas = pd.read_excel(FNAME, sheet_name="Listas")

# 4) Extrae listas de palabras clave
puestos       = listas["Puestos"]                 .dropna().str.lower().tolist()
materiales    = listas["Materiales"]              .dropna().str.lower().tolist()
comp_blandas  = listas["Competencias Blandas"]    .dropna().str.lower().tolist()
comp_tecnicas = listas["Competencias Técnicas"]   .dropna().str.lower().tolist()

# 5) Funciones de búsqueda y extracción
def first_match(text, keywords):
    t = str(text).lower()
    for kw in keywords:
        if kw in t:
            return kw
    return ""

def all_matches(text, keywords):
    t = str(text).lower()
    return ", ".join([kw for kw in keywords if kw in t])

def extract_experience(text):
    t = str(text).lower()
    m = re.search(r"(?:más de\s*|\+)?\s*(\d{1,2})\s*años?", t)
    if not m:
        return ""
    num = m.group(1)
    raw = m.group(0)
    return f"+{num}" if raw.strip().startswith(("más de", "+")) else num

# 6) Concatenar columnas A–E en "__todo__"
def concat_row(row):
    def safe(x):
        return "" if pd.isna(x) else str(x)
    parts = [
        safe(row.get("Nombre/Título")),
        safe(row.get("Link LinkedIn")),
        safe(row.get("Extracto")),
        safe(row.get("Años de experiencia")),
        safe(row.get("Materiales"))
    ]
    return " ".join([p for p in parts if p])

df["__todo__"] = df.apply(concat_row, axis=1)

# 7) Generar DataFrame limpio
clean = pd.DataFrame({
    "Orden":                 range(1, len(df)+1),
    "Nombre Completo":       df["Nombre/Título"],
    "Cargo Actual":          df["__todo__"].apply(lambda t: first_match(t, puestos)),
    "Carrera Profesional":   df["Extracto"],
    "Años de Experiencia":   df["Extracto"].apply(extract_experience),
    "Materiales":            df["__todo__"].apply(lambda t: all_matches(t, materiales)),
    "Competencias Blandas":  df["__todo__"].apply(lambda t: all_matches(t, comp_blandas)),
    "Competencias Técnicas": df["__todo__"].apply(lambda t: all_matches(t, comp_tecnicas)),
})

# 8) Escribir en la hoja “Tabla Limpia”
with pd.ExcelWriter(FNAME, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
    clean.to_excel(writer, sheet_name="Tabla Limpia", index=False)

print(f"✅ Generados {len(clean)} registros en la hoja 'Tabla Limpia'.")
