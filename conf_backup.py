from netmiko import ConnectHandler
from jinja2 import Environment, FileSystemLoader
import yaml


def j2_command(file_name, directory='.'):
    env = Environment(loader=FileSystemLoader(directory))
    temp = env.get_template(file_name)
    temp_1 = temp.render()
    temp_1 = temp_1.split('\n')
    return temp_1


def get_host_name(open_connection):
    hostname = open_connection.find_prompt()
    hostname = hostname.split('#')[0]
    return hostname


def write_to_file(data, device_connection):
    with open(f'./output/config_{get_host_name(device_connection)}.txt', 'w') as conf:
        conf.write(data)


with open('inventory.yml') as f:
    host_obj = yaml.safe_load(f)

generic_data = host_obj[0]['generic_data']
generic_username = generic_data['username']
generic_password = generic_data['password']
devices = host_obj[0]['devices']

device_ip = devices[0]['ip_address']
device_type = generic_data['device_type']
device_secret = generic_data['secret']

print(devices)

for device in devices:
    try:
        if device["username"]: generic_username = device['username']
        if device['password']: generic_password = device['password']
        if device["device_type"]: device_type = device['device_type']
        if device['secret']: device_secret = device['secret']

    except:
        pass

    dev = {
        'device_type': device_type,
        'host': device_ip,
        'username': generic_username,
        'password': generic_password,
        'secret': device_secret
    }

    connect = ConnectHandler(**dev)
    commands = j2_command('script.j2')
    output = ''

    for command in commands:
        breaker = f'\n\n\n\n\n##########################  {command}  ##########################\n\n\n\n\n'
        output += breaker + connect.send_command(command)

    print(get_host_name(connect))
    write_to_file(output, connect)
