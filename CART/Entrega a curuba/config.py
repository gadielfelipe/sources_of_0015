# =============================================================================
# config.py  –  Parámetros globales del pipeline de pronóstico
# =============================================================================
# Edita SOLO este archivo antes de cada corrida.

import os

# ── Rutas ─────────────────────────────────────────────────────────────────────
MODEL_DIR = r'C:\Users\Usuario\OneDrive - Global Green Growth Institute\Documentos\Gadiel\Aplicacion\OneDrive_1_21-3-2026\nuevos'

# ── Archivos de modelos (fijos, no cambian entre corridas) ────────────────────
MODEL_PATH       = os.path.join(MODEL_DIR, 'xgb_empeoro.pkl')
MEDIAN_PATH      = os.path.join(MODEL_DIR, 'median_train.pkl')
FEAT_COLS_PATH   = os.path.join(MODEL_DIR, 'feature_cols.pkl')

# ── Archivos de entrada (CAMBIAN cada corrida) ────────────────────────────────
CARTERA_FILE  = 'Informe_Cartera_ENERO2026.xlsx'        # <-- actualizar
CALIF_FILE    = 'CalCartera_Analisis_UTRAHUILCA DIC2025.xlsx'  # <-- actualizar

CARTERA_PATH  = os.path.join(MODEL_DIR, CARTERA_FILE)
CALIF_PATH    = os.path.join(MODEL_DIR, CALIF_FILE)
CALIF_SHEET   = 'Analisis_Cal_Cartera'

# ── Parámetros del modelo ─────────────────────────────────────────────────────
BEST_THRESH = 0.35   # umbral de clasificación; ajustar si es necesario

# ── Columnas de features ──────────────────────────────────────────────────────
NUM_COLS = [
    'CUOTAS PAGADAS', 'AMORTIZACIÓN', 'MODIFICACIONES',
    'TASA INTERÉS NOMINAL', 'TASA INTERÉS EFECTIVA',
    'VALOR PRÉSTAMO', 'VALOR CUOTA', 'SALDO CAPITAL', 'SALDO INTERESES',
    'GARANTÍA', 'CONTINGENCIA', 'VALOR APORTES SOCIALES',
    'INGRESOS ACTUALES', 'INGRESOS AÑO ANTERIOR', 'ACTIVOS', 'PASIVOS',
    'PROVISION_CON_CALIFICACION_SUPER_MAYOR_20%',
    'ValorMora_Entidad', 'ValorMora_Mercado',
    'Score_CP', 'Score_Sol', 'Score_Gar', 'Score_SD',
    'Score_Rest', 'Score_CI', 'Score_PE',
    'RCI', 'CFT', 'NET', 'VI', 'RS', 'CA', 'CG',
    'DM', 'DSP', 'DELTA_CAL', 'SPREAD_MORA',
    'RIESGO_SECTOR', 'RIESGO_ACTIVIDAD',
    'FLAG_ARRASTRE', 'NIVEL_RIESGO', 'MOD', 'MOD_CE', 'DET_MOD',
]

CAT_COLS = [
    'TIPO CUOTA', 'MODALIDAD', 'PERIODICIDAD AMORTIZACIÓN',
    'DESTINO CRÉDITO', 'TIPO VIVIENDA', 'CLASE GARANTÍA',
    'ACTIVIDAD ECONÓMICA DEUDOR', 'SECTOR ECONOMICO',
    'Peor_Cal_Entidad', 'Peor_Cal_Mercado',
    'AlturaMora_Entidad', 'AlturaMora_Mercado',
    'INSOLVENCIA', 'RIESGO',
    'RANGO PARTICIPACIÓN ENTIDAD EN ENDEUDAMIENTO GLOBAL DEL CLIENTE',
]

# ── Garantías admisibles ──────────────────────────────────────────────────────
GARANTIAS_ADMISIBLES = [
    '1-HIPOTECA', '5-PRENDARIA', '6-CERTIFICADO GARANTIAS(FRGT)',
    '2-APORTES SOCIALES', '11-FAG', '16-FONDO DE GARANTIAS(FAG ESPECIA',
    '17-FNG (Unidos por el cambio EMP3', '14-PIGNORACION DE CONTRATOS',
    '12-CESION DE DERECHOS',
]

# ── Mapas de riesgo ───────────────────────────────────────────────────────────
RIESGO_SECTOR = {
    'JUBILADOS PENSIONADOS': 0, 'EDUCACION': 0,
    'SECTOR OFICIAL Y FUERZA PUBLICA': 0, 'SALUD': 0,
    'INTERMEDIACION FINANCIERA': 1, 'SERVICIOS Y OTRAS ACTIVIDADES': 1,
    'CONSUMO (COMERCIO)': 1, 'MANUFACTURA': 1,
    'INMOBILIARIAS Y DE ALQUILER': 1, 'SECTOR ECONOMIA SOLIDARIA (NO FINANCIERO)': 1,
    'AGRICOLA': 2, 'PECUARIO': 2, 'TRANSPORTE': 2,
    'CONSTRUCCION Y VIVIENDA': 2, 'HOTELES, RESTAURANTES, BARES Y SIMILARES': 2,
    'MINERO Y ENERGETICO': 3,
}

RIESGO_ACTIVIDAD = {
    'JUBILADO PENSIONADO': 0, 'ASALARIADO': 0, 'DEPENDIENTE': 0,
    'PROFESIONAL INDEPENDIENTE': 1, 'INDEPENDIENTE FORMALIZADO': 1, 'PERSONA JURIDICA': 1,
    'INDEPENDIENTE AGROPECUARIO': 2, 'INDEPENDIENTE INFORMAL': 2, 'EMPLEADA DOMESTICA': 2,
}
