import json
import paramiko

sshClient = paramiko.SSHClient()

sshClient.load_system_host_keys()


def ler_json(file: str):
    with open(file, encoding='utf8') as json_file:
        return json.load(json_file)


hosts = ler_json("private/devices.json")

interface = "lan"
idVlan = 230
aliasVlan = f"OFFICE_{idVlan}"
addressInterface = f"10.10.{idVlan}.1"
Mask = "255.255.255.0"
Gateway = f"10.10.{idVlan}.1"
startIpRange = f"10.10.{idVlan}.2"
endIpRange = f"10.10.{idVlan}.254"

script = f'''
        config vdom \n
        edit root \n

        config system interface \n
            edit VLAN_{idVlan} \n
                set alias {aliasVlan} \n
                set vlanid {idVlan} \n 
                set vdom root \n
                set interface "lan" \n
                set type vlan \n
                set ip {addressInterface} 255.255.255.0 \n
                set allowaccess ping \n
            next \n
        end \n

        config system dhcp server \n
            edit {idVlan} \n
                set dns-service default \n
                set default-gateway {Gateway} \n
                set netmask {Mask} \n
                set interface "VLAN_{idVlan}" \n

                config ip-range \n
                    edit 1 \n
                        set start-ip {startIpRange} \n
                        set end-ip {endIpRange} \n
                end \n
            end \n

        config system interface \n
            edit VLAN_{idVlan} \n
            show \n
    '''

sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

for item in hosts['devices']:
    try:
        sshClient.connect(item['host'], item['port'] or 22,
                          item['user'], item['password'])

        print('''
        ===========================================================
        --------------- {} ---------------
        ===========================================================
        '''.format(item['name']))
    except:
        print("erro ao conectar")

    stdin, stdout, stderr = sshClient.exec_command(script)

    stdin.write('''
        config system interface \n
            edit VLAN_{idVlan} \n
            show \n
    ''')

    stdin.flush()

    for line in stdout:
        print(line)

    sshClient.close()
