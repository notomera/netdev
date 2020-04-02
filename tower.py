from jinja2 import Environment, FileSystemLoader
import yaml
import asyncio
import netdev


def j2_command(file_name: dict = 'script.j2', directory: str = '.') -> dict:
    env = Environment(loader=FileSystemLoader(directory))
    temp = env.get_template(file_name)
    temp_1 = temp.render()
    temp_1 = temp_1.split('\n')
    return temp_1


def get_host_name(open_connection) -> str:
    hostname = hostname.split('#')[0]
    return hostname


def write_to_file(data, dev_name):
    name = dev_name['host']
    with open(f'./output/config_{name}.txt', 'w+') as conf:
        conf.write(data)


def load_yml(yaml_file='inventory.yml'):
    with open(yaml_file) as f:
        host_obj = yaml.safe_load(f)
    return host_obj

async def device_connection(connect_param, conf_type = 'command'):
    
    dev_connect = netdev.create(**connect_param)
    ip_address = connect_param['host']
    await dev_connect.connect()    
    commands = j2_command()
    output = [f'\n\n\n\n\n##########################  {ip_address} ##########################\n\n\n\n\n']
    if conf_type == 'config':
        command_result = await dev_connect.send_command(commands)
        return command_result
    else:
        for command in commands:
            breaker = f'\n\n\n\n\n##########################  {command}  ##########################\n\n\n\n\n'
            command_result = await dev_connect.send_command(command)
            output.append(breaker + command_result)
        
        output_result_string = "\n\n".join(output)
    
    return output_result_string

def dev_data():
    device_data = []
    host_obj = load_yml()

    generic_data = host_obj[0]['generic_data']
    generic_username = generic_data['username']
    generic_password = generic_data['password']
    devices = host_obj[0]['devices']
    device_type = generic_data['device_type']
    device_secret = generic_data['secret']
    for device in devices:
        device_ip = device['ip_address']
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
        # print(dev)

        device_data.append(dev)

    return device_data


if __name__ == '__main__':
    device_data = dev_data()
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(device_connection(dev)) 
        for dev in device_data
    ]
    loop.run_until_complete(asyncio.wait(tasks))
    for name, task in zip(device_data, tasks):
        write_to_file(task.result(), name)
