from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest, start_http_server, Summary, Gauge, Enum
from flask import Flask, request, Response
import time
from exception.ToolException import FailException
import yaml
import model.get_power
import model.get_inventory
import model.get_temperature
import model.get_health

registry = CollectorRegistry()

# Metrics description
probe_status = Enum('probe_status', 'Probe status', ['target'], states=['up', 'down'], registry=registry)
temperature_gauge = Gauge('temperature_celsius', 'Temperature in Celsius', ['target', 'type'], registry=registry)
health_gauge = Gauge('syshealth', 'Health status (1: Healthy, 0: Unhealthy)', ['target', 'type'], registry=registry)
inventory_number_gauge = Gauge('inventory_number', 'Number of inventory items', ['target', 'type'], registry=registry)
power_usage_gauge = Gauge('power_usage_watts', 'Power usage in watts', ['target', 'type'], registry=registry)

app = Flask(__name__)

class Args:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

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
        user = ipmi_info[ip]['pm_user']
        password = ipmi_info[ip]['pm_password']
        args = Args(host=ip, port=port, username=user, password=password)
        for mod in module.split(','):
            if mod == 'inventory':
                inventory_number_gauge._metric_init()
                inventory = model.get_inventory.GetInventory()
                inventory.run(args)
                for key, value in inventory.dict.items():
                    inventory_number_gauge.labels(target=target, type=key).set(value)
                probe_status.labels(target=target).state('up')
            elif mod == 'temperature':
                temperature_gauge._metric_init()
                temperature = model.get_temperature.GetTemperature()
                temperature.run(args)
                for temp in temperature.temperatures:
                    temperature_gauge.labels(target=target, type=temp.name).set(temp.reading_celsius)
                probe_status.labels(target=target).state('up')
            elif mod == 'health':
                health_gauge._metric_init()
                health = model.get_health.GetHealth()
                health.run(args)
                for key, value in health.dict.items():
                    health_gauge.labels(target=target, type=key).set(1 if value == 'OK' else 0)
                probe_status.labels(target=target).state('up')
            elif mod == 'power':
                power_usage_gauge._metric_init()
                power = model.get_power.GetPower()
                power.run(args)
                for key, value in power.dict.items():
                    if value != None:
                        power_usage_gauge.labels(target=target, type=key).set(value)
                probe_status.labels(target=target).state('up')
            else:
                probe_status.labels(target=target).state('down')
                return Response(f"Bad request: Invalid module '{mod}'", status=400)
    except FailException as e:
        probe_status.labels(target=target).state('down')
        return Response(f"Error: {e}", status=500)
    
    return Response(generate_latest(registry), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9119)