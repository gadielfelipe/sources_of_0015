import pandas as pd
import numpy as np
import dreqPy
import os
print(os.path.dirname(dreqPy.__file__))

from dreqPy import dreq

dq = dreq.loadDreq()

print("version",dq.version)
print("len",len(dq.inx.uid))


from dreqPy import dreq
dq = dreq.loadDreq()

from dreqPy import dreq
import pandas as pd
import shutil
import dreqPy
import os

base_path = os.path.dirname(dreqPy.__file__)
print("Base path:", base_path)

print("\nArchivos en dreqPy:")
for f in os.listdir(base_path):
    print(" -", f)


from dreqPy import dreq

dq = dreq.loadDreq()
print(dq)
# Exportar el XML completo
#dq.writeXml("dreq.xml")

#print("XML exportado como dreq.xml")
dq = dreq.loadDreq()

# Variables
vars = dq.coll['var'].items

# Experimentos
exps = dq.coll['experiment'].items

# Enlaces variable–escenario
links = dq.coll['requestLink'].items

print(vars)

target_vars = ["tas", "pr", "txx", "r95p"]

print("Segunda etapa")
for v in dq.coll['var'].items:
    if v.label in target_vars:
        print(v.label, "-", v.title)
