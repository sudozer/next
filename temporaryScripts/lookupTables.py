import json
import pdb

fpath = '/home/jacob/share/next/packetDefinitions/o2o_tlm_db_new.pd'
defDict = json.load(open(fpath,'r'))

enums = {}

enums['enumToPatState'] = {
        0: "0: STANDBY",
        1: "1: INIT",
        2: "2: MANUALTEST",
        10: "10: LOCAL_POINT",
        11: "11: LOCAL_SLEW",
        12: "12: INERTIAL_POINT",
        13: "13: ACQ_SPIRAL",
        14: "14: ACQ_PULLIN",
        20: "20: COARSE_TRACK_LOW",
        21: "21: COARSE_TRACK_MED",
        30: "30: FINE_TRACK",
        31: "31: FINE_TRACK_HOM_DITHER",
        32: "32: FINE_TRACK_HOM_CENTER",
        100: "100: CAL",
        101: "101: CAL_COARSETRACK_LBM",
        102: "102: CAL_FINETRACK_HOM",
        103: "103: CAL_DONE",
        254: "254: FAULT_SOFT",
        255: "255: FAULT_HARD"
    }

enums['enumToPayloadActivity'] = {
        0: "0: IDLE",
        16: "16: STANDBY",
        17: "17: GIMBAL_HOLD",
        32: "32: OPERATE",
        33: "33: POP",
        34: "34: SLEW",
        35: "35: ACTIVE",
        36: "36: SELF_TEST",
        37: "37: CALIBRATE",
        38: "38: LASERCOM",
        127: "127: FTP_TEST"
    }

enums['enumToPointingToolStatus'] = {
        0: '0: POINTING AT EARTH',
        1: '1: NOT POINTING AT EARTH',
        2: '2: DEBUG',
        255: '255: UNINITIALIZED'
    }

enums['enumToElSign'] = {
        0: '0: NEGATIVE',
        1: '1: POSITIVE'
    }

enums['enumToStStarIdStatus'] = {
        0: '0: IDLE',
        1: '1: INITIALIZE',
        2: '2: WAITING_FOR_IMAGE1',
        3: '3: WAITING_FOR_IMAGE2',
        4: '4: CALCULATE_RATE',
        5: '5: MAKE_UNIT_VECTORS',
        6: '6: AWAITING_TRISTAR',
        7: '7: OK_FOUND_4',
        8: '8: OK_FOUND_3',
        9: '9" TIME_OUT',
        10: '10: TBD',
        11: '11: NO_MATCH'
    }

for pkt in defDict:
    for field in defDict[pkt]['fields']:
        if 'conversion' in field:
            for conversionFunction in enums:
                if field['conversion']['conversionFunction'] == conversionFunction:
                    field['conversion']['conversionFunction'] = 'lookupTable'
                    field['conversion']['conversionArgs']=[enums[conversionFunction]]

json.dump(defDict,open(fpath,'w'),indent=4)