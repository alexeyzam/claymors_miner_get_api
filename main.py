import socket
import json
from pyzabbix import ZabbixMetric, ZabbixSender


def get_miner_stat(method):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('192.168.1.99', 3335))
    message=json.dumps({"id": 1, "jsonrpc": "2.0", "method": method})
    message=f'{message}\n'
    s.sendall(message.encode("utf-8"))

    data = json.loads(s.recv(1024).decode("utf-8"))['result']
    s.close()
    return data


if __name__ == '__main__':
    packet = []
    try:
        stat1 = get_miner_stat("miner_getstat1")
        stat2 = get_miner_stat("miner_getstat2")
        packet.append(ZabbixMetric('fs1.zmrn.ru', 'claymor_live', 1))
        i = 0
        GPU_HR = {}
        GPU_LIST = stat1[3].split(';')
        GPU_POWER_FAN = stat1[6].split(';')
        packet.append(ZabbixMetric('fs1.zmrn.ru', 'claymor_uptime', int(stat1[1])))

        for i in range(len(GPU_LIST)):
            GPU_HR[i] = int(GPU_LIST[i]) * 1000
            packet.append(ZabbixMetric('fs1.zmrn.ru', f'GPU_{i}_claymor_hashrate', int(GPU_LIST[i]) * 1000))
        packet.append(ZabbixMetric('fs1.zmrn.ru', 'Total_power_usage_claymor_miner', int(stat2[17])))

        for i in range(len(GPU_POWER_FAN)):
            GPU_NUM = int(i / 2)
            if GPU_NUM * 2 == i:
                packet.append(ZabbixMetric('fs1.zmrn.ru', f'GPU_{GPU_NUM}_claymor_FanSpeed', GPU_POWER_FAN[i]))
            else:
                packet.append(ZabbixMetric('fs1.zmrn.ru', f'GPU_{GPU_NUM}_claymor_Temp', GPU_POWER_FAN[i]))

        packet.append(ZabbixMetric('fs1.zmrn.ru', 'claymor_active_mining_pool', stat1[7]))
        zbx = ZabbixSender('192.168.1.101')
        zbx.send(packet)
    except (ConnectionRefusedError, OSError):
        packet.append(ZabbixMetric('fs1.zmrn.ru', 'claymor_live', 0))
        zbx = ZabbixSender('192.168.1.101')
        zbx.send(packet)
