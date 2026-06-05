from datetime import datetime
import sys
import json
import logging

sys.path.append('../utils')
from loadConfig import Configs
cfgLoader = Configs()
CONFIG = cfgLoader.loadGlobalConfig

class BrokenPackets():
    def __init__(self,logLevel=logging.WARNING):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(filename=CONFIG()['logBasepath'], encoding='utf-8',level=logLevel)

    def logBrokenPacket(self,pkt,template,errStr):
        #TODO log bad packets in a way that they can be readily analyzed later
        print("packet logging not yet implemented")