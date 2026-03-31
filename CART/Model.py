import pandas as pd
import os 
import numpy as np

os.chdir("C://Users//Usuario//OneDrive - Global Green Growth Institute//Documentos//Gadiel//Aplicacion//OneDrive_1_21-3-2026")
print(os.listdir())
cartera=pd.read_excel("Informe_Cartera_9744.xlsx", header=4)
print(cartera.shape)
print(cartera.head())
print(cartera.columns)


