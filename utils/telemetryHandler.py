
import datetime
import logging
import pdb
import sys

sys.path.append('../utils')
sys.path.append('../decode')
sys.path.append('../convert')
sys.path.append('../store')

from loadConfig import Configs
cfgLoader = Configs()
CONFIG = cfgLoader.loadGlobalConfig
from decode import Decoder
from convert import Converter
from store import Storage

from brokenPackets import BrokenPackets


class TelemetryHandler():
    def __init__(self,packetStructure,logLevel=logging.WARNING):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(filename=CONFIG()['logBasepath'], encoding='utf-8', level=logLevel)
        self.decoder = Decoder(packetStructure,logLevel)
        self.converter = Converter(logLevel)
        self.storage = Storage(logLevel)
        self.packetStructure = packetStructure
        self.brokenPacketHandler = BrokenPackets(logLevel)
    
    def decodeConvertStore(self,packet,groundTimeStamp = True):
        self.logger.debug(f"Received packet: {packet}")
        decodedPacket = self.decoder.readPacket(packet)
        if decodedPacket:
            self.logger.debug(f"Decoded packet:\n\n{decodedPacket}")

            if groundTimeStamp:
                if 'metadata' in decodedPacket:
                    decodedPacket['metadata']['groundTimestampUTC'] = datetime.datetime.now(datetime.UTC).strftime(CONFIG()['datetimeFormat'])
                else:
                    decodedPacket['metadata'] = {'groundTimestampUTC': datetime.datetime.now(datetime.UTC).strftime(CONFIG()['datetimeFormat'])}

            convertedPacket = self.converter.convertPacket(decodedPacket)
            #TODO fix primary timestamp in case user decides to use a different primary timestamp from the converted packets
            convertedPacket['metadata']['primaryTimestamp'] = decodedPacket['metadata']['groundTimestampUTC']
            self.logger.debug(f"Converted packet:\n\n{convertedPacket}")
            
            self.storage.storePacket(convertedPacket)
            return convertedPacket
        else:
            self.logger.warning(f"Failed to decode packet: {packet}")
            self.brokenPacketHandler.logMalformedPacket(self.packetStructure,packet)
            return False
    
    def decodeConvertStoreList(self,packetList):
        convertedPackets = []
        for packet in packetList:
            convertedPacket = self.decodeConvertStore(packet)
            if convertedPacket:
                convertedPackets.append(convertedPacket)
        return convertedPackets


