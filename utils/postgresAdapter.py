import psycopg
from psycopg import sql
import json
from pathlib import Path
import pdb
from loadConfig import Configs
cfgLoader = Configs()
CONFIG = cfgLoader.loadGlobalConfig

class PGConnection():
    def __init__(self):
        self.pgInfo = CONFIG()['postgres']
        self.connectionString = f"host={self.pgInfo['host']} dbname={self.pgInfo['dbName']} user={self.pgInfo['user']} password={self.pgInfo['password']}"
        self.loadDefinitions()
    def createDexUser(self):
        #must be run as postgres
        pdb.set_trace()
        conn = psycopg.connect(
        dbname="postgres",
        user="postgres", 
        host="localhost",
        autocommit=True  # Bypasses open transaction blocks
        )

        new_username = self.pgInfo['user']
        new_password = self.pgInfo['password']

        try:
            with conn.cursor() as cur:
                # 2. Use sql.Identifier and sql.Placeholder to prevent injection
                query = sql.SQL(f"CREATE USER {self.pgInfo['user']} WITH PASSWORD \'{self.pgInfo['password']}\'")
                
                # 3. Execute the statement
                cur.execute(query, (new_password,))
                print(f"User '{new_username}' created successfully.")

        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            conn.close()

    def createDatabase(self):
        pdb.set_trace()
        dbCreationString = f"host={self.pgInfo['host']} dbname=postgres user={self.pgInfo['user']} password={self.pgInfo['password']}"
        with psycopg.connect(dbCreationString, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE {self.pgInfo['dbName']};")
                cur.execute(f"ALTER DATABASE {self.pgInfo['dbName']} SET timezone TO \'UTC\';")
    
    def initPacketTable(self):
        with psycopg.connect(self.connectionString) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                CREATE TABLE IF NOT EXISTS packets (
                packetID UUID PRIMARY KEY,
                primaryTimestamp TIMESTAMPTZ NOT NULL,
                telemetryStructure VARCHAR(30) NOT NULL,
                components TEXT NOT NULL
                );
                """)

    def initDatatagTable(self):
        with psycopg.connect(self.connectionString) as conn:
            with conn.cursor() as cur:
                cur.execute("""
      component                CREATE TABLE IF NOT EXISTS datatags (
                tagID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                primaryTimestamp TIMESTAMPTZ NOT NULL,
                telemetryStructure VARCHAR(30) NOT NULL,
          s TEXT NOT NULL
                );
                """)

    def initFieldTable(self,key,storageLevel=1):
        pdb.set_trace()
        if storageLevel == 1:
            queryString = f"""
                CREATE TABLE IF NOT EXISTS {key}(
                packetID UUID PRIMARY KEY,
                primaryTimestamp TIMESTAMPTZ NOT NULL,
                rawBits BIT({field['bitLength']}) NOT NULL,
                );
                """

        with psycopg.connect(self.connectionString) as conn:
            with conn.cursor() as cur:
                cur.execute(queryString)

    def loadDefinitions(self):

        tdefPath = Path(CONFIG()['telemetryDefinitionsBasepath'])
        files = [f for f in tdefPath.rglob('*') if f.is_file() and f.suffix in ('.hd')]
        self.telemetryDefinitions = {}

        for telemetryDefinitionFile in files:
            self.telemetryDefinitions[telemetryDefinitionFile.name] = json.load(open(telemetryDefinitionFile,'r'))       
            
        files = [f for f in tdefPath.rglob('*') if f.is_file() and f.suffix in ('.pd')]
        for telemetryDefinitionFile in files:
            self.telemetryDefinitions[telemetryDefinitionFile.name] = json.load(open(telemetryDefinitionFile,'r'))

    def addRecords(self,fields,storageLevel=1,conn = None):
        
        openConnection = True
        if not conn:
            openConnection = False
            conn = psycopg.connect(self.connectionString)
        
        key = f"{fields[0]['source']}::{fields[0]['fieldName']}"
        cur = conn.cursor()

        if storageLevel == 1:
            queryString = f"INSERT INTO {key} (packetID,primaryTimestamp,rawBits) VALUES (%s, %s, %s)"
            data = [(x['packetUUID'],x['primaryTimestamp'],x['rawBits']) for x in fields]
        
        cur.executemany(queryString,data)
        conn.commit()
        
        if not openConnection:
            cur.close()
            conn.close()
