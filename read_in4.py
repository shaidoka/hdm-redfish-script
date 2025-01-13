import yaml
import subprocess

with open('/etc/kolla/masakari-engine/inventory.yaml', 'r') as yml_file:
    config = yaml.safe_load(yml_file)

with open('/home/pam.trungvb2/hdm-redfish-script/ipaddress.txt', 'r') as ip_file:
    ip_addresses = [line.strip() for line in ip_file.readlines()]

ip_info = {node['pm_addr']: node for node in config['nodes']}

# Thực hiện lệnh cho mỗi địa chỉ IP
for ip in ip_addresses:
    if ip in ip_info:
        user = ip_info[ip]['pm_user']
        password = ip_info[ip]['pm_password']
        command = f"python3 main.py -H {ip} -p 443 -U {user} -P '{password}' getproductinfo | grep -i Serial"
        subprocess.run(command, shell=True)
    else:
        print(f"Thông tin cho địa chỉ IP {ip} không được tìm thấy trong cấu hình.")