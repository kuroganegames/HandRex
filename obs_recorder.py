#coding:utf-8

import subprocess
from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher
from configparser import ConfigParser
# obsclipy_ws.py
import obsws_python as obs
from ipaddress import ip_address, IPv6Address

class OBSWSController:
    def __init__(self, host_ip: str = "127.0.0.1", port: int = 4455, password: str = ""):
        self.client = obs.ReqClient(host=host_ip, port=int(port), password=password)

    def record_start(self):
        print("start record!")
        # すでに録画中か確認してから開始
        if not self.client.get_record_status().output_active:
            self.client.start_record()
        else:
            print("already recording")

    def record_end(self):
        print("end record!")
        status = self.client.get_record_status()
        if status.output_active:
            self.client.stop_record()
            # print(f"saved to: {status.output_path}")  # ファイル名が取れる
            # print(dir(status))
            # print(status.output_paused)
            print("saved!")



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

def normalize_ip(addr: str) -> str:
    """
    IPv6 アドレスなら [ ] を付与して URI 形式に合わせる。
    すでに [] が付いている場合や IPv4 は変更しない。
    """
    if addr.startswith('['):          # 既に角括弧付き
        return addr
    try:
        if isinstance(ip_address(addr), IPv6Address):
            return f'[{addr}]'        # IPv6 だけ括る
    except ValueError:
        pass                          # ホスト名などはそのまま
    return addr

    
if __name__=="__main__":
    #設定ファイル「setting.ini」を読み込みます。
    config_ini = ConfigParser()
    config_ini.read("setting.ini", encoding="utf-8")

    IP_OBS = normalize_ip(config_ini['OBS']['IP'])
    PORT_OBS = config_ini['OBS']['PORT']
    PASS_OBS = config_ini['OBS']['PASS']
    
    IP_VRC = normalize_ip(config_ini['VRCosc']['IP'])
    PORT_VRC = int(config_ini['VRCosc']['PORT'])
    
    print("-----\n[OBS]\nip: {}\nport: {}\npass: {}\n[VRChat]\nIP: {}\nPORT: {}\n-----".format(IP_OBS, PORT_OBS, PASS_OBS, IP_VRC, PORT_VRC))
    
    # ocp = obsclipy(i_port, s_pass)
    ocp = OBSWSController(IP_OBS, PORT_OBS, PASS_OBS)

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
    server = osc_server.ThreadingOSCUDPServer((IP_VRC, PORT_VRC), dispatcher)
    print(f"Serving on {server.server_address}")
    server.serve_forever()