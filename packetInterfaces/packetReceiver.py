import json
import sys
import logging
sys.path.append('../utils')
sys.path.append('../packetDefinitions')

from packetDefinitionLib import PacketDefinitionUtility
from loadConfig import Configs
CFGLOADER = Configs()
CONFIG = CFGLOADER.loadGlobalConfig

class PktReceiver():
    def __init__(self,packetType,logLevel=logging.WARNING):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(filename=CONFIG()['logBasepath'], encoding='utf-8', level=logLevel)
        self.packetType = packetType
        self.pktDefUtil = PacketDefinitionUtility(logLevel)
        self.validatePacketType(packetType)

    def validatePacketType(self,packetType):
        #throw a tantrum if databases fail validation
        if not packetType in CONFIG()['telemetryStructures']:
            self.logger.error(f"{packetType} not a recognized packet type.  Current packets types are: {CONFIG()['telemetryStructures'].keys()}")
        validatedDataType = True
        for pktDefPath in CONFIG()['telemetryStructures'][packetType]['format']:
            if not self.pktDefUtil.validateDefinitionFile(pktDefPath):
                validatedDataType = False
                self.logger.error(f"Invalid packet definition file: {pktDefPath} in {packetType} packet structure.")
        if validatedDataType:
            self.logger.info(f"Definition files for {packetType} fully validated.")
            return True
        else:
            return False