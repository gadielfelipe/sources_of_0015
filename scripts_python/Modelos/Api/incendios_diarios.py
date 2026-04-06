"""
incendios_diarios.py
Descarga los puntos de calor del día anterior desde IDEAM y los agrega
al archivo Excel histórico. Diseñado para ejecutarse con el Programador
de tareas de Windows una vez al día.
"""

import requests
import pandas as pd
import io
import urllib3
import logging
from datetime import date, timedelta
from pathlib import Path

# ─── Logging ────────────────────────────────────────────────────────────────
LOG_FILE = Path(__file__).parent / "incendios_diarios.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)
log = logging.getLogger(__name__)

# ─── Configuración ──────────────────────────────────────────────────────────
TARGET_DATE = date.today() - timedelta(days=1)
DATE_STR    = TARGET_DATE.strftime("%Y-%m-%d")

REGION   = "colombia"
EXTENT   = "11.781325296112277_-86.94580078125_-1.8234225930141486_-65.43457031250001"

BASE_URL     = "https://puntosdecalor.ideam.gov.co/"
DOWNLOAD_URL = f"{BASE_URL}download-result/"

OUTPUT_DIR  = Path(r"C:\Users\Usuario\OneDrive - Global Green Growth Institute\Documentos\2025\Outputs\Output4\Indicadores\Incendios")
OUTPUT_FILE = OUTPUT_DIR / "incendios diarios.xlsx"

# ─── Descarga ────────────────────────────────────────────────────────────────
def descargar(date_str: str) -> pd.DataFrame:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    referer = (
        f"{BASE_URL}?from_date={date_str}&to_date={date_str}"
        f"&region={REGION}&extent=({EXTENT})"
    )
    headers = {
        "Referer": referer,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/csv,application/octet-stream,*/*",
    }
    log.info(f"GET {DOWNLOAD_URL}  |  fecha={date_str}")
    resp = requests.get(DOWNLOAD_URL, headers=headers, timeout=60, verify=False)
    resp.raise_for_status()

    df = pd.read_csv(io.StringIO(resp.text), sep=";", decimal=",", encoding="utf-8")
    df.insert(0, "fecha_descarga", pd.to_datetime(date_str))
    log.info(f"Descargados {len(df):,} puntos de calor para {date_str}.")
    return df


# ─── Guardar en Excel ────────────────────────────────────────────────────────
def guardar(df_new: pd.DataFrame) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if OUTPUT_FILE.exists():
        df_existing = pd.read_excel(OUTPUT_FILE, engine="openpyxl")
        if "fecha_descarga" not in df_existing.columns:
            df_existing.insert(0, "fecha_descarga", pd.NaT)
        df_existing["fecha_descarga"] = pd.to_datetime(df_existing["fecha_descarga"], errors="coerce")

        fechas_existentes = df_existing["fecha_descarga"].dropna().dt.date.unique()
        if TARGET_DATE in fechas_existentes:
            log.warning(f"Fecha {DATE_STR} ya existe en el archivo. No se agregan duplicados.")
            print(f"[AVISO] {DATE_STR} ya fue descargado anteriormente. Nada que hacer.")
            return

        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new.copy()

    df_combined.to_excel(OUTPUT_FILE, index=False, engine="openpyxl")
    log.info(f"Archivo guardado: {OUTPUT_FILE}  ({len(df_combined):,} filas totales)")
    print(f"[OK] Guardado: {OUTPUT_FILE}  –  {len(df_combined):,} filas totales")


# ─── Main ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Procesando puntos de calor para: {DATE_STR}")
    try:
        df = descargar(DATE_STR)
        if df.empty:
            log.warning(f"Sin datos para {DATE_STR}.")
            print(f"[AVISO] No se encontraron puntos de calor para {DATE_STR}.")
        else:
            guardar(df)
            # Resumen rápido en consola
            fuente_col = next((c for c in df.columns if "fuente" in c.lower()), None)
            if fuente_col:
                print(df[fuente_col].value_counts().to_string())
    except Exception as exc:
        log.error(f"Error: {exc}", exc_info=True)
        print(f"[ERROR] {exc}")
        raise
