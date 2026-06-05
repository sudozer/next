import json
import pdb

def append_bitlengths(packet):
    for field in packet['fields']:
        match field['type']:
            case "uint8_t" | "int8_t":
                baseFieldLength = 8
            case "uint16_t" | "int16_t":
                baseFieldLength = 16
            case "uint32_t" | "int32_t":
                baseFieldLength = 32
            case "uint64_t" | "int64_t":
                baseFieldLength = 64  
            case "float":
                baseFieldLength = 32
            case "double":
                baseFieldLength = 64
            case "char":
                baseFieldLength = 8
        if 'arrayLength' in field:
            field['bitLength'] = baseFieldLength * field['arrayLength']
        else:
            field['bitLength'] = baseFieldLength
    return packet

cmdFile = open("cmd/o2o_cmd_db.json", "r")
tlmFile = open("tlm/o2o_tlm_db.json", "r")
cmdData = json.load(cmdFile)
newCMD = {}
tlmData = json.load(tlmFile)
newTLM = {}

for packet in cmdData['Packets']:
    newCMD[packet['packetId']] = append_bitlengths(packet)

for packet in tlmData['Packets']:
    newTLM[packet['packetId']] = append_bitlengths(packet)


with open("cmd/o2o_cmd_db_new.pd", "w") as cmdOut:
    json.dump(newCMD, cmdOut, indent=4)

with open("tlm/o2o_tlm_db_new_2.pd", "w") as tlmOut:
    json.dump(newTLM, tlmOut, indent=4)
    

        