import socket
import json
from pyzabbix import ZabbixMetric, ZabbixSender


def get_miner_stat(method):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('192.168.1.98', 3333))
    s.sendall(json.dumps({"id": 0, "jsonrpc": "2.0", "method": method}).encode("utf-8"))
    data = json.loads(s.recv(1024).decode("utf-8"))['result']
    s.close()
    return data


if __name__ == '__main__':
    stat1 = get_miner_stat("miner_getstat1")
    stat2 = get_miner_stat("miner_getstat2")
    i = 0
    GPU_HR = {}
    GPU_LIST = stat1[3].split(';')
    GPU_POWER_FAN = stat1[6].split(';')
    print(GPU_POWER_FAN)
    packet = []
    for i in range(len(GPU_LIST)):
        GPU_HR[i] = int(GPU_LIST[i]) * 1000
        packet.append(ZabbixMetric('fs1.zmrn.ru', f'GPU_{i}_claymor_hashrate', int(GPU_LIST[i]) * 1000))
    packet.append(ZabbixMetric('fs1.zmrn.ru', f'Total_power_usage_claymor_miner', int(stat2[17])))

    for i in range(len(GPU_POWER_FAN)):
        GPU_NUM = int(i / 2)
        if GPU_NUM * 2 == i:
            packet.append(ZabbixMetric('fs1.zmrn.ru', f'GPU_{GPU_NUM}_claymor_FanSpeed', GPU_POWER_FAN[i]))
        else:
            packet.append(ZabbixMetric('fs1.zmrn.ru', f'GPU_{GPU_NUM}_claymor_Temp', GPU_POWER_FAN[i]))

    zbx = ZabbixSender('192.168.1.101')
    zbx.send(packet)
