from orbitProp import OrbitProp
import csv
import pdb
from pathlib import Path

#pdb.set_trace()
ascPath = Path('../ascFiles')
productPath = Path('../dataProducts/ephemerisComparison.csv')
asFlownData = OrbitProp()
asFlownData.readASC("../ascFiles/asFlown.asc")
files = [f for f in ascPath.iterdir() if f.is_file()]

predictData = OrbitProp()
for file in files:
    if not 'asFlown' in str(file):
        predictData.readASC(file)

with open(productPath,'w',newline='') as outFile:
    writer = csv.writer(outFile)
    writer.writerow(['predict_timestamp','predict_ICRF_X','predict_ICRF_Y','predict_ICRF_Z','predict_ICRF_VX','predict_ICRF_VY','predict_ICRF_VZ','asFlown_ICRF_X','asFlown_ICRF_Y','asFlown_ICRF_Z','asFlown_ICRF_VX','asFlown_ICRF_VY','asFlown_ICRF_VZ'])

    for row in predictData.ephemeris:

        asFlownInterpolation = tuple(asFlownData.propagateTo(row['timestamp']))
        rowlist = [row['timestamp'],row['x'],row['y'],row['z'],row['vx'],row['vy'],row['vz']]
        writer.writerow(rowlist + list(asFlownInterpolation))
        