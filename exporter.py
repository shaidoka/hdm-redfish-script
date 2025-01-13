from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest, start_http_server, Summary, Gauge, Enum
from flask import Flask, request, Response
import time
from utils.client import RedfishClient, RestfulClient
from exception.ToolException import FailException
import yaml
import model.get_power
import model.get_inventory
import model.get_temperature

registry = CollectorRegistry()

# Metrics description
probe_status = Enum('probe_status', 'Probe status', ['target'], states=['up', 'down'], registry=registry)
temperature_gauge = Gauge('temperature_celsius', 'Temperature in Celsius', ['target'], registry=registry)
inventory_number_gauge = Gauge('inventory_number', 'Number of inventory items', ['target', 'type'], registry=registry)

app = Flask(__name__)

with open('/etc/kolla/masakari-engine/inventory.yaml', 'r') as yml_file:
    masakari_inventory = yaml.safe_load(yml_file)

ipmi_info = {node['pm_addr']: node for node in masakari_inventory['nodes']}

@app.route('/probe')
def probe():
    target = request.args.get('target')
    module = request.args.get('module')

    if not target or not module:
        return Response("Bad request: Missing 'target' or 'module' params", status=400)
    
    probe_status._metric_init()

    try:
        ip = target.split(':')[0]
        port = target.split(':')[1]
        client = RedfishClient({'host': ip, 'port': port, 'user': ipmi_info[ip]['pm_user'], 'password': ipmi_info[ip]['pm_password']})
        for mod in module.split(','):
            if mod == 'inventory':
                inventory_number_gauge._metric_init()
                inventory = model.get_inventory.GetInventory()
                inventory.run(client)
                for key, value in inventory.dict.items():
                    inventory_number_gauge.labels(target=target, type=key).set(value)
            elif mod == 'temperature':
                temperature_gauge._metric_init()
                temperature = model.get_temperature.GetTemperature()
                temperature.run(client)
                temperature_gauge.labels(target=target).set(temperature.temperature)
            else:
                return Response(f"Bad request: Invalid module '{mod}'", status=400)
    except FailException as e:
        probe_status.labels(target=target).state('down')
        return Response(f"Error: {e}", status=500)
    
    return Response(generate_latest(registry), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9119)