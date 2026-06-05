"""
This file contains the final conversions for data being decoded from packets.
At this point a packet is received, the bits have been split into their appropriate fields,
and data the data has been interpreted to a primitive data type.

This set of functions performs any further necessary manipulation of the data in those fields.
"""
import logging
import sys
import pdb
import json

sys.path.append('../utils')
from brokenPackets import BrokenPackets
import conversionFunctions
from loadConfig import Configs
cfgLoader = Configs()
CONFIG = cfgLoader.loadGlobalConfig

class Converter():
    def __init__(self,logLevel=logging.WARNING):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(filename=CONFIG()['logBasepath'], encoding='utf-8', level=logLevel)
        self.brokenPacketLogger = BrokenPackets(logLevel)
        self.brokenPacket = False
    def convertField(self,field):

        try:
            conversionFunc = field['conversion']['conversionFunction']
            conversionArgs = field['conversion']['conversionArgs']
            conversionVal = field['rawValue']
            if hasattr(conversionFunctions,conversionFunc):
                callString = f"conversionFunctions.{conversionFunc}({conversionVal},{conversionArgs})"
                field['convertedValue'] = eval(callString)
                return field
            else:
                self.logger.error(f"Conversion function: {conversionFunc} not present in conversionFunctions.py file.\n\nError encountered when converting field:\n{json.dumps(field,indent=4)}.\n\nAvaliable conversion functions: {dir(conversionFunctions)}")
                return field
        except Exception as E:
            self.logger.error(f"Error when converting field:\n{json.dumps(field,indent=4)}\n\n{str(E)}")
            self.brokenPacket = True
            return field

    def convertPacket(self,decodedPacket):
        self.brokenPacket = False
        for fld in decodedPacket:
            field = decodedPacket[fld]
            if 'conversion' in field:
                decodedPacket[fld] = self.convertField(field)
        # if self.brokenPacket:
        #     self.brokenPacketLogger.logBrokenPacket(decodedPacket,fld,)
        return decodedPacket
            