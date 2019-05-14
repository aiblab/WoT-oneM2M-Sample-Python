#!/usr/bin/python
import os
import os.path
import configparser

class Config:
    
    def __init__(self):
        self.BaseURL = ""
        self.Origin = ""
        self.PoA = ""

    def loadProperties(self, filepath):
        if 'VCAP_SERVICES' in os.environ:
            import json
            vcap_services = json.loads(os.environ['VCAP_SERVICES'])
            handypia_iot = vcap_services['HandyPIA-IoT-Platform'][0]
            cred = handypia_iot['credentials']
            m2murl = cred['onem2mBaseUrl']
            self.BaseURL = m2murl
            self.PoA = ''
            words = m2murl.split('/')
            self.Origin = words[len(words)-2]
        elif os.path.isfile(filepath):
            parser = configparser.RawConfigParser()
            parser.read(filepath)
            self.BaseURL = parser.get('DEFAULT', 'oneM2M_scl_base_url')
            self.Origin = parser.get('DEFAULT', 'oneM2M_scl_base_origin')
            self.PoA = parser.get('DEFAULT', 'oneM2M_poa_url')
        else:
            raise FileNotFoundError(filepath)

        if not self.BaseURL:
            raise ValueError("oneM2M_scl_base_url is empty")
        if not self.Origin:
            raise ValueError("oneM2M_scl_base_origin is empty")

