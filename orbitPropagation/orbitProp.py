import satkit
import polars as pl
from pathlib import Path
import datetime
import csv
import pdb
import numpy as np

class OrbitProp:
    def __init__(self):
        self.ephemeris = pl.DataFrame(schema={"timestamp":pl.Datetime, "x":pl.Float64, "y":pl.Float64, "z":pl.Float64, "vx":pl.Float64, "vy":pl.Float64, "vz":pl.Float64})
        self.latestState = None

    def addEph(self, x, y, z, vx, vy, vz, timestamp):
        newEph = {"x": x, "y": y, "z": z, "vx": vx, "vy": vy, "vz": vz, "timestamp": timestamp}
        self.ephemeris = self.ephemeris.append(newEph)
        if timestamp > self.ephemeris[-1]['timestamp']:
            self.updateEph(newEph)
        else:
            self.ephemeris.sort('timestamp')

    def updateEph(self,eph):
        self.latestState, self.latestTimestamp = self.packArray(eph)

    def packArray(self,eph):
        array = np.array([eph['x'],eph['y'],eph['z'],eph['vx'],eph['vy'],eph['vz'],])
        time_ = eph['timestamp'][0]
        return array,time_
    
    def readASC(self,fname):
        print(fname)
        self.dateFormatString = "%Y-%m-%dT%H:%M:%S.%f%Z"
        with open(fname,'r') as f:
            reader = csv.reader(f, delimiter=' ')
            dataDict = {"timestamp":[], "x":[], "y":[], "z":[], "vx":[], "vy":[], "vz":[]}
            for row in reader:
                try:
                    #if the first element is a timestamp, than this is a data row
                    dataDict["timestamp"].append(datetime.datetime.strptime(row[0]+"UTC", self.dateFormatString))
                    dataDict["x"].append(float(row[1]) * 1000)
                    dataDict["y"].append(float(row[2]) * 1000)
                    dataDict["z"].append(float(row[3]) * 1000)
                    dataDict["vx"].append(float(row[4]) * 1000)
                    dataDict["vy"].append(float(row[5]) * 1000)
                    dataDict["vz"].append(float(row[6]) * 1000)
                except:
                    continue
        self.ephemeris = self.ephemeris.vstack(pl.DataFrame(dataDict)).sort("timestamp")
        self.updateEph(self.ephemeris[-1])

    def propagateTo(self, targetTime):
        minPropSec = 10
        #find nearest ephemeris point to targetTime
        if targetTime > self.ephemeris['timestamp'][-1]:
            state = self.latestState
            stateTime = self.latestTimestamp
        elif targetTime < self.ephemeris['timestamp'][0]:
            state,stateTime = self.packArray(self.ephemeris[0])
        else:
            #find closest ephemeris point before targetTime

            before = self.ephemeris.filter(pl.col("timestamp") <= targetTime).sort("timestamp", descending=True)[0]
            after = self.ephemeris.filter(pl.col("timestamp") >= targetTime).sort("timestamp")[0]
            if targetTime - before["timestamp"][0] < after["timestamp"][0] - targetTime:
                nearest = before
            else:
                nearest = after
            #propagate from before to target time
            state,stateTime = self.packArray(nearest)
            
        if abs(stateTime - targetTime) < minPropSec:
            return state
        
        try:
            propagatedState = satkit.propagate(state,satkit.time.from_datetime(stateTime),end=satkit.time.from_datetime(targetTime))
        except:
            pdb.set_trace()
        return propagatedState.state
    
    

    