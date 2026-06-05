import json
import pdb
with open('../packetDefinitions/o2o_tlm_db_new.pd', 'r') as f:
    data = json.load(f)

types = []
conversions = []
for pktID in data:
    for field in data[pktID]['fields']:
        if field['type'] not in types:
            types.append(field['type'])
        if 'conversion' in field:
            try:
                if not field['conversion']['conversionFunction'] in conversions:
                    conversions.append(field['conversion']['conversionFunction'])
            except:
                pass
            try:
                if not field['conversion']['deconversionFunction'] in conversions:
                    conversions.append(field['conversion']['deconversionFunction'])
            except:
                pass


    
print(types)
print(conversions)
