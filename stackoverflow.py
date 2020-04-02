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
    hostname = open_connection.base_prompt()
    hostname = hostname.split('#')[0]
    return hostname


def write_to_file(data, dev_conn):
    with open(f'./output/config_{get_host_name(dev_conn)}.txt', 'w') as conf:
        conf.write(data)


def load_yml(yaml_file='inventory.yml'):
    with open(yaml_file) as f:
        host_obj = yaml.safe_load(f)
    return host_obj


async def device_connection(connect_param):
    dev_connect = netdev.create(**connect_param)
    await dev_connect.connect()
    commands = j2_command()
    output = [f'\n\n\n\n\n##########################  1'
              f'  ##########################\n\n\n\n\n']

    for command in commands:
        breaker = f'\n\n\n\n\n##########################  {command}  ##########################\n\n\n\n\n'
        command_result = await dev_connect.send_command(command)
        output.append(breaker + command_result)
    await dev_connect.disconnect()
    output_result_string = "\n\n".join(output)
    return output_result_string


def dev_data():
    device_data = []
    # devices_names = []
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
        print(dev)

        device_data.append(dev)

    return device_data


async def main(device_data):
    tasks = [device_connection(dev) for dev in device_data]
    result = await asyncio.gather(task for task in tasks)
    return result




if __name__ == '__main__':
    r = asyncio.run(main(dev_data()))
    print(r)