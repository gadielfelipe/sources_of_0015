# =============================================================================
# pipeline.py  –  Funciones modulares del pipeline de pronóstico
# =============================================================================
# Estructura:
#   1. cargar_artefactos()       → carga modelo, mediana y feature_cols
#   2. cargar_datos()            → lee y hace merge de cartera + calificación
#   3. construir_features()      → genera todas las variables del modelo
#   4. preparar_X()              → alinea columnas y aplica imputación
#   5. predecir()                → genera probabilidades y etiquetas
#   6. exportar_resultado()      → guarda el Excel con nombre automático
#   7. run_pipeline()            → orquesta todo (punto de entrada)

import os
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

import config


# =============================================================================
# 1. CARGAR ARTEFACTOS DEL MODELO
# =============================================================================
def cargar_artefactos():
    """
    Carga el modelo XGBoost, la mediana de entrenamiento y las columnas de features.
    Retorna: (model, median_train, feature_cols)
    """
    print("[1/6] Cargando artefactos del modelo...")
    model        = joblib.load(config.MODEL_PATH)
    median_train = joblib.load(config.MEDIAN_PATH)
    feature_cols = joblib.load(config.FEAT_COLS_PATH)
    print(f"      Features esperados: {len(feature_cols)}")
    return model, median_train, feature_cols


# =============================================================================
# 2. CARGAR Y UNIR DATOS DEL NUEVO PERÍODO
# =============================================================================
def cargar_datos():
    """
    Lee Informe_Cartera y CalCartera, hace el merge y retorna el DataFrame base.
    """
    print("[2/6] Cargando datos del nuevo período...")

    cartera = pd.read_excel(config.CARTERA_PATH, header=0)
    df_calif = pd.read_excel(config.CALIF_PATH, sheet_name=config.CALIF_SHEET)

    print(f"      Cartera: {cartera.shape[0]:,} registros")
    print(f"      Calificación: {df_calif.shape[0]:,} registros")

    # Homologar tipo de ID
    cartera["IDETIFICACIÓN"]  = cartera["IDETIFICACIÓN"].astype(str)
    df_calif["NUMERO_ID"]     = df_calif["NUMERO_ID"].astype(str)
    df_calif = df_calif.drop_duplicates(subset="NUMERO_ID")

    cols_calif = [
        "NUMERO_ID",
        "CALIF_DE_ARRASTRE_SUPER_MAYOR_20%",
        "PROVISION_CON_CALIFICACION_SUPER_MAYOR_20%",
        "RANGO PARTICIPACIÓN ENTIDAD EN ENDEUDAMIENTO GLOBAL DEL CLIENTE",
        "AlturaMora_Entidad", "AlturaMora_Mercado",
        "ValorMora_Entidad",  "ValorMora_Mercado",
        "Peor_Cal_Entidad",   "Peor_Cal_Mercado",
        "INSOLVENCIA", "RIESGO",
    ]

    df = cartera.merge(
        df_calif[cols_calif],
        left_on="IDETIFICACIÓN",
        right_on="NUMERO_ID",
        how="left",
    )

    print(f"      Registros después del merge: {df.shape[0]:,}")
    return df


# =============================================================================
# 3. CONSTRUCCIÓN DE FEATURES
# =============================================================================
def construir_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica exactamente el mismo pipeline de features que se usó en entrenamiento.
    Modifica el DataFrame in-place y lo retorna.
    """
    print("[3/6] Construyendo features...")

    # Fecha de corte
    fecha_corte = pd.to_datetime(
        df[['VIGENCIA', 'MES', 'DÍA']].rename(
            columns={'VIGENCIA': 'year', 'MES': 'month', 'DÍA': 'day'}
        )
    )

    # ── 1. Capacidad de pago ──────────────────────────────────────────────────
    df['RCI'] = np.where(df['INGRESOS ACTUALES'] > 0,
        df['VALOR CUOTA'] / df['INGRESOS ACTUALES'], np.nan)
    df['CFT'] = np.where(df['INGRESOS ACTUALES'] > 0,
        (df['VALOR CUOTA'] + df['SALDO INTERESES']) / df['INGRESOS ACTUALES'], np.nan)
    df['VI']  = np.where(df['INGRESOS AÑO ANTERIOR'] > 0,
        (df['INGRESOS ACTUALES'] - df['INGRESOS AÑO ANTERIOR']) / df['INGRESOS AÑO ANTERIOR'], np.nan)
    df['NET'] = np.where(df['ACTIVOS'] > 0, df['PASIVOS'] / df['ACTIVOS'], np.nan)

    for col in ['RCI', 'CFT', 'VI', 'NET']:
        df[col] = df[col].clip(upper=df[col].quantile(0.99))

    df['Score_CP'] = (
        (df['RCI'] > 0.30).astype(int) +
        (df['CFT'] > 0.40).astype(int) +
        (df['NET'] > 0.70).astype(int) +
        (df['VI']  < 0.00).astype(int)
    )

    # ── 2. Solvencia ──────────────────────────────────────────────────────────
    df['RS'] = np.where(df['PASIVOS'] > 0, df['ACTIVOS'] / df['PASIVOS'], np.nan)
    deuda_entidad = df['SALDO CAPITAL'] + df['SALDO INTERESES'] + df['OTROS SALDOS']
    df['CA'] = np.where(deuda_entidad > 0, df['ACTIVOS'] / deuda_entidad, np.nan)

    for col in ['RS', 'CA']:
        df[col] = df[col].clip(upper=df[col].quantile(0.99))

    df['INSOLVENCIA'] = pd.to_numeric(df['INSOLVENCIA'], errors='coerce').fillna(0).astype(int)

    df['Score_Sol'] = (
        (df['RS'] < 1.0).astype(int) +
        (df['CA'] < 1.0).astype(int) +
        (df['INSOLVENCIA'] == 1).astype(int)
    )

    # ── 3. Garantías ──────────────────────────────────────────────────────────
    df['CG'] = np.where(df['SALDO CAPITAL'] > 0,
        df['GARANTÍA'] / df['SALDO CAPITAL'], np.nan)
    df['CG'] = df['CG'].clip(upper=df['CG'].quantile(0.99))

    df['GA'] = np.where(
        df['DETALLE GARANTÍA'].astype(str).str.strip().isin(config.GARANTIAS_ADMISIBLES), 1, 0)

    df['FECHA AVALÚO'] = pd.to_datetime(df['FECHA AVALÚO'], errors='coerce')
    df['AA'] = ((fecha_corte - df['FECHA AVALÚO']).dt.days / 30).clip(lower=0)
    df['AA'] = df['AA'].clip(upper=df['AA'].quantile(0.99))

    penaliza_CG = ((df['GA'] == 1) & (df['CG'] < 1.0)).astype(int)
    penaliza_AA = ((df['GA'] == 1) & (df['AA'] > 48)).astype(int)
    df['Score_Gar'] = (df['GA'] == 0).astype(int) + penaliza_CG + penaliza_AA

    # ── 4. Servicio de la deuda ───────────────────────────────────────────────
    df['DM'] = (
        pd.to_numeric(df['AlturaMora_Entidad'], errors='coerce')
        .fillna(pd.to_numeric(df['MOROSIDAD'], errors='coerce'))
        .clip(lower=0)
    )
    df['FECHA ÚLTIMO PAGO'] = pd.to_datetime(df['FECHA ÚLTIMO PAGO'], errors='coerce')
    df['DSP'] = ((fecha_corte - df['FECHA ÚLTIMO PAGO']).dt.days).clip(lower=0)
    df['DSP'] = df['DSP'].clip(upper=df['DSP'].quantile(0.99))

    df['Score_SD'] = (
        (df['DM'] > 30).astype(int) +
        (df['DM'] > 90).astype(int) +
        (df['DSP'] > 60).astype(int)
    )

    # ── 5. Reestructuraciones ─────────────────────────────────────────────────
    df['MOD'] = (pd.to_numeric(df['MODIFICACIONES'], errors='coerce').fillna(0) > 0).astype(int)
    df['MOD_CE'] = (
        (df['MODIFICACIONES DEL CRÉDITO CE 11/20'].astype(str).str.strip().isin(['0', 'nan']) == False) |
        (df['MODIFICACIONES AL CRÉDITO CE 17/20'].astype(str).str.strip().isin(['0', 'nan']) == False)
    ).astype(int)
    df['DET_MOD'] = 0  # sin target en producción

    df['Score_Rest'] = df['MOD'] + df['MOD_CE'] + df['DET_MOD']

    # ── 6. Centrales de información ───────────────────────────────────────────
    cal_map = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
    df['Peor_Cal_Mercado_n'] = df['Peor_Cal_Mercado'].map(cal_map)
    df['Peor_Cal_Entidad_n'] = df['Peor_Cal_Entidad'].map(cal_map)
    df['DELTA_CAL'] = (df['Peor_Cal_Mercado_n'] - df['Peor_Cal_Entidad_n']).fillna(0)

    df['ValorMora_Mercado'] = pd.to_numeric(df['ValorMora_Mercado'], errors='coerce').fillna(0)
    df['ValorMora_Entidad'] = pd.to_numeric(df['ValorMora_Entidad'], errors='coerce').fillna(0)
    df['SPREAD_MORA'] = (df['ValorMora_Mercado'] - df['ValorMora_Entidad']).clip(lower=0)
    df['SPREAD_MORA'] = df['SPREAD_MORA'].clip(upper=df['SPREAD_MORA'].quantile(0.99))

    df['FLAG_ARRASTRE'] = pd.to_numeric(
        df['CALIF_DE_ARRASTRE_SUPER_MAYOR_20%'], errors='coerce').fillna(0).clip(0, 1).astype(int)

    riesgo_map = {'Riesgo_Bajo': 0, 'Riesgo_Medio': 1, 'Riesgo_Alto': 2, 'Riesgo_Muy_Alto': 3}
    df['NIVEL_RIESGO'] = df['RIESGO'].map(riesgo_map).fillna(1)

    df['Score_CI'] = (
        (df['DELTA_CAL']      > 0).astype(int) +
        (df['SPREAD_MORA']    > 0).astype(int) +
        (df['FLAG_ARRASTRE'] == 1).astype(int) +
        (df['INSOLVENCIA']   == 1).astype(int) +
        (df['NIVEL_RIESGO']   > 1).astype(int)
    )

    # ── 7. Perspectivas económicas ────────────────────────────────────────────
    df['RIESGO_SECTOR']    = df['SECTOR ECONOMICO'].map(config.RIESGO_SECTOR).fillna(1)
    df['RIESGO_ACTIVIDAD'] = df['ACTIVIDAD ECONÓMICA DEUDOR'].map(config.RIESGO_ACTIVIDAD).fillna(1)

    df['Score_PE'] = (
        (df['RIESGO_SECTOR']    >= 2).astype(int) +
        (df['RIESGO_SECTOR']    == 3).astype(int) +
        (df['RIESGO_ACTIVIDAD'] >= 2).astype(int)
    )

    print("      Features construidos correctamente.")
    return df


# =============================================================================
# 4. PREPARAR MATRIZ X
# =============================================================================
def preparar_X(df: pd.DataFrame, feature_cols: list, median_train) -> pd.DataFrame:
    """
    Arma X_nuevo con las columnas exactas del entrenamiento,
    aplica get_dummies en categóricas e imputa con la mediana de entrenamiento.
    """
    print("[4/6] Preparando matriz X...")

    X = pd.concat([
        df[config.NUM_COLS],
        pd.get_dummies(df[config.CAT_COLS], drop_first=True),
    ], axis=1)

    # Alinear columnas al entrenamiento (agrega las que falten con 0)
    X = X.reindex(columns=feature_cols, fill_value=0)

    # Imputar infinitos y nulos con mediana de entrenamiento
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(median_train).fillna(0)

    print(f"      Shape de X: {X.shape}")
    return X


# =============================================================================
# 5. GENERAR PRONÓSTICO
# =============================================================================
def predecir(df: pd.DataFrame, X: pd.DataFrame, model, thresh: float) -> pd.DataFrame:
    """
    Agrega prob_empeoro y pred_empeoro al DataFrame original.
    """
    print(f"[5/6] Generando pronóstico (umbral={thresh})...")

    df['prob_empeoro'] = model.predict_proba(X)[:, 1]
    df['pred_empeoro'] = (df['prob_empeoro'] >= thresh).astype(int)

    total   = len(df)
    en_riesgo = df['pred_empeoro'].sum()
    print(f"      Créditos en riesgo de empeorar: {en_riesgo:,} de {total:,} ({en_riesgo/total:.1%})")

    print(df[['CODCUE', 'IDETIFICACIÓN', 'prob_empeoro', 'pred_empeoro']]
          .sort_values('prob_empeoro', ascending=False)
          .head(20)
          .to_string(index=False))

    return df


# =============================================================================
# 6. EXPORTAR RESULTADO
# =============================================================================
def exportar_resultado(df: pd.DataFrame) -> str:
    """
    Guarda el Excel con nombre automático basado en la fecha del sistema.
    Retorna la ruta del archivo generado.
    """
    print("[6/6] Exportando resultado...")

    fecha_str  = datetime.now().strftime("%Y%m%d_%H%M")
    nombre     = f"pronostico_{fecha_str}.xlsx"
    ruta_salida = os.path.join(config.MODEL_DIR, nombre)

    df.to_excel(ruta_salida, index=False)
    print(f"      Archivo guardado en: {ruta_salida}")
    return ruta_salida


# =============================================================================
# 7. PIPELINE COMPLETO (punto de entrada)
# =============================================================================
def run_pipeline(thresh: float = config.BEST_THRESH) -> str:
    """
    Orquesta todas las etapas del pronóstico.
    Parámetro:
        thresh: umbral de clasificación (default desde config.py)
    Retorna:
        ruta del archivo Excel generado
    """
    print("=" * 60)
    print("PIPELINE DE PRONÓSTICO – INICIO")
    print(f"Cartera  : {config.CARTERA_FILE}")
    print(f"Calif.   : {config.CALIF_FILE}")
    print(f"Umbral   : {thresh}")
    print("=" * 60)

    model, median_train, feature_cols = cargar_artefactos()
    df  = cargar_datos()
    df  = construir_features(df)
    X   = preparar_X(df, feature_cols, median_train)
    df  = predecir(df, X, model, thresh)
    out = exportar_resultado(df)

    print("=" * 60)
    print("PIPELINE COMPLETADO")
    print("=" * 60)
    return out


# =============================================================================
# EJECUCIÓN DIRECTA (validación local)
# =============================================================================
if __name__ == "__main__":
    run_pipeline()
