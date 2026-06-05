import satkit
import polars as pl
from pathlib import Path
import datetime
import csv

class orbitProp:
    def __init__(self, sourceFile):
        self.sourceFile = sourceFile

    def addEph(self, x, y, z, vx, vy, vz, timestamp):
        newEph = {"x": x, "y": y, "z": z, "vx": vx, "vy": vy, "vz": vz, "timestamp": timestamp}
        self.ephemeris = self.ephemeris.append(newEph)
        self.updateEph(newEph)

    def updateEph(self,eph):
        self.sat = satkit.Satellite.from_state_vector(eph["x"], eph["y"], eph["z"], eph["vx"], eph["vy"], eph["vz"], epoch=eph["timestamp"])

    def readASC(self):
        self.dateFormatString = "%Y-%m-%dT%H:%M:%S.%f%Z"
        pl.dataframe()
        with open(self.sourceFile,'r') as f:
            reader = csv.reader(f, delimiter=' ')
        dataDict = {"timestamp":[], "x":[], "y":[], "z":[], "vx":[], "vy":[], "vz":[]}
        for row in reader:
            try:
                #if the first element is a timestamp, than this is a data row
                dataDict["timestamp"].append(datetime.datetime.strptime(row[0], self.dateFormatString))
                dataDict["x"].append(float(row[1]))
                dataDict["y"].append(float(row[2]))
                dataDict["z"].append(float(row[3]))
                dataDict["vx"].append(float(row[4]))
                dataDict["vy"].append(float(row[5]))
                dataDict["vz"].append(float(row[6]))
            except:
                continue
        self.ephemeris = pl.DataFrame(dataDict)
        self.updateEph(self.ephemeris[-1])

    def propagateTo(self, targetTime):
        #find nearest ephemeris point to targetTime
        if targetTime > self.ephemeris['timestamp'] [-1]:
            propagatedState = self.sat.propagate(targetTime)
            return propagatedState
    
        else:
            #find closest ephemeris point before targetTime
            before = self.ephemeris.filter(pl.col("timestamp") <= targetTime).sort("timestamp", descending=True).first()
            after = self.ephemeris.filter(pl.col("timestamp") >= targetTime).sort("timestamp").first()
            if targetTime - before["timestamp"] < after["timestamp"] - targetTime:
                nearest = before
            else:
                nearest = after
            #propagate from before to target time
            sat = satkit.Satellite.from_state_vector(nearest["x"], nearest["y"], nearest["z"], nearest["vx"], nearest["vy"], nearest["vz"], epoch=nearest["timestamp"])
            propagatedState = sat.propagate(targetTime)
            return propagatedState
    
    