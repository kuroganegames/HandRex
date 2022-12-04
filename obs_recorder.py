#coding:utf-8

import subprocess
from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher
from configparser import ConfigParser



# obs-cliを動かすためのクラス
class obsclipy:
    def __init__(self, port="4444", password="password"):
        self.i_port = port
        self.s_pass = password
        
    def record_start(self):
        print("start record!")
        return subprocess.run(["obs-cli", "recording", "start", "--password", self.s_pass, "--port", self.i_port])
    def record_end(self):
        print("end record")
        return subprocess.run(["obs-cli", "recording", "stop", "--password", self.s_pass, "--port", self.i_port])



    
if __name__=="__main__":
    #設定ファイル「setting.ini」を読み込みます。
    config_ini = ConfigParser()
    config_ini.read("setting.ini", encoding="utf-8")

    i_port = config_ini['OBS']['PORT']
    s_pass = config_ini['OBS']['PASS']
    
    IP = config_ini['VRCosc']['IP']
    PORT = int(config_ini['VRCosc']['PORT'])
    
    
    
    ocp = obsclipy(i_port, s_pass)

    # oscで受信した時の関数です
    def obs_handler(unused_addr, isRecord):
        
        print(f"recieved {isRecord}")
        if isRecord:
            ocp.record_start()
        else:
            ocp.record_end()




    #osc通信の設定
    dispatcher = Dispatcher()
    dispatcher.map("/avatar/parameters/recording", obs_handler)

    #受信サーバーを動かす
    server = osc_server.ThreadingOSCUDPServer((IP, PORT), dispatcher)
    print(f"Serving on {server.server_address}")
    server.serve_forever()