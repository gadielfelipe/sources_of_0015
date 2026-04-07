"""
actualizar_dashboard.py
Orquestador diario del dashboard ERIS – GGGI Colombia.
Ejecuta cada notebook/script existente en orden y registra el resultado.
"""

import subprocess
import sys
import logging
from datetime import datetime
from pathlib import Path

# ─── Rutas ────────────────────────────────────────────────────────────────────
BASE = Path(r"C:\Users\Usuario\OneDrive - Global Green Growth Institute\Documentos\2025\Outputs\Output1\Stress Test\3.Data\Scripts Python")

PYTHON  = sys.executable
JUPYTER = [PYTHON, "-m", "jupyter", "nbconvert", "--to", "notebook",
           "--execute", "--inplace", "--ExecutePreprocessor.timeout=600"]

TAREAS = [
    {
        "nombre": "Precipitacion diaria (datos_municipios.csv)",
        "tipo": "notebook",
        "ruta": BASE / "scripts_python" / "Modelos" / "Api" / "appi diaria datos precipitacion.ipynb",
    },
    {
        "nombre": "Puntos de calor – Incendios (incendios_ultimo_dia.csv)",
        "tipo": "py",
        "ruta": BASE / "scripts_python" / "Modelos" / "Api" / "incendios_diarios.py",
    },
    {
        "nombre": "Incendios – cruce municipal + exportar CSV web",
        "tipo": "notebook",
        "ruta": BASE / "scripts_python" / "Incendios.ipynb",
    },
    {
        "nombre": "Amenazas deslizamientos (amenazas_municipal.csv)",
        "tipo": "notebook",
        "ruta": BASE / "scripts_python" / "Movimientos de tierra.ipynb",
    },
]

# ─── Logging ──────────────────────────────────────────────────────────────────
LOG_FILE = Path(__file__).parent / "actualizacion_dashboard.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)
log = logging.getLogger(__name__)

# ─── Ejecución ────────────────────────────────────────────────────────────────
def ejecutar_tarea(tarea: dict) -> bool:
    nombre = tarea["nombre"]
    ruta   = tarea["ruta"]

    if not ruta.exists():
        log.warning(f"OMITIDO – archivo no encontrado: {ruta}")
        print(f"  ⚠  Omitido (no encontrado): {ruta.name}")
        return False

    if tarea["tipo"] == "notebook":
        cmd = JUPYTER + [str(ruta)]
    else:
        cmd = [PYTHON, str(ruta)]

    log.info(f"INICIO  – {nombre}")
    print(f"  →  {nombre} ...", flush=True)
    t0 = datetime.now()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        elapsed = (datetime.now() - t0).seconds

        if result.returncode == 0:
            log.info(f"OK      – {nombre}  ({elapsed}s)")
            print(f"     ✓  OK  ({elapsed}s)")
            return True
        else:
            log.error(f"ERROR   – {nombre}  ({elapsed}s)\n{result.stderr[-1000:]}")
            print(f"     ✗  ERROR ({elapsed}s) – ver log: {LOG_FILE.name}")
            return False

    except Exception as exc:
        log.error(f"EXCEPCION – {nombre}: {exc}", exc_info=True)
        print(f"     ✗  EXCEPCION: {exc}")
        return False


if __name__ == "__main__":
    inicio = datetime.now()
    log.info("=" * 60)
    log.info(f"INICIO ACTUALIZACION DASHBOARD  {inicio:%Y-%m-%d %H:%M:%S}")
    log.info("=" * 60)
    print(f"\nActualizando dashboard ERIS – {inicio:%Y-%m-%d %H:%M}\n")

    resultados = []
    for tarea in TAREAS:
        ok = ejecutar_tarea(tarea)
        resultados.append((tarea["nombre"], ok))

    # Resumen
    ok_count  = sum(1 for _, ok in resultados if ok)
    err_count = len(resultados) - ok_count
    elapsed   = (datetime.now() - inicio).seconds

    print(f"\n{'─'*50}")
    print(f"  Completado: {ok_count}/{len(resultados)} tareas OK  ({elapsed}s)")
    if err_count:
        print(f"  {err_count} tarea(s) con error – revisar {LOG_FILE.name}")
    print(f"{'─'*50}\n")

    log.info(f"FIN  {ok_count}/{len(resultados)} OK  {elapsed}s")
    log.info("=" * 60)

    sys.exit(0 if err_count == 0 else 1)
