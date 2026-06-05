
import sys
import logging
sys.path.append('../utils')

from loadConfig import Configs
cfgLoader = Configs()
CONFIG = cfgLoader.loadGlobalConfig

from rxPorts import TCPClient
from telemetryHandler import TelemetryHandler
from packetReceiver import PktReceiver
class tcpReciever(PktReceiver):
    def __init__(self,ip,port,packetType,logLevel=logging.WARNING):
        super().__init__(packetType,logLevel)
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(filename=CONFIG()['logBasepath'], encoding='utf-8', level=logLevel)
        self.packetHandler = TelemetryHandler(packetType,logLevel)
        self.TCPRX = TCPClient(ip,port,self.packetHandler.decodeAndStore,logLevel)
        self.TCPRX.listen()
