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
    ephRow = 0
    firstPredictTimestamp = predictData.ephemeris[0]['timestamp']
    asFlowni = 0
    while asFlownData.ephemeris[asFlowni]['timestamp'] < firstPredictTimestamp:
        asFlowni += 1

    for row in predictData.ephemeris:

        rowlist = [row['timestamp'],row['x'],row['y'],row['z'],row['vx'],row['vy'],row['vz']]
        if asFlowni < len(asFlownData.ephemeris) and asFlownData.ephemeris[asFlowni]['timestamp'] < row['timestamp']:
            asFlown = asFlownData.ephemeris[asFlowni]
            asFlownList = [asFlown['timestamp'],asFlown['x'],asFlown['y'],asFlown['z'],asFlown['vx'],asFlown['vy'],asFlown['vz']]
            writer.writerow(rowlist + asFlownList)
            asFlowni += 1
        else:
            writer.writerow(rowlist)
        