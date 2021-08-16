from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from netmiko.ssh_exception import SSHException
from netmiko.ssh_exception import AuthenticationException

import re

# here is list of cisco devices ip addresses
ip_list = open("D:\\Python\\IPAddressList.txt")

import logging
logging.basicConfig(filename='devicelogging1.log', level=logging.DEBUG)

# list where informations will be stored
devices = []

# clearing the old data from the CSV file and writing the headers
f = open("Inventory.csv", "w+")
f.write("IP Address, Hostname, Uptime, Current_Version, Current_Image, Serial_Number, Device_Model, Device_Memory")
f.write("\n")
f.close()

# clearing the old data from the CSV file and writing the headers
f = open("Login_Issue.csv", "w+")
f.write("IP Address, Status")
f.write("\n")
f.close()

# loop all ip addresses in ip_list
for ip in ip_list:
    ip = ip.strip()
    cisco = {
        'device_type': 'cisco_ios',
        'ip': ip,
        'username': 'Username',  # ssh username
        'password': 'Pass',  # ssh password
        'secret': 'Pass',  # ssh_enable_password
        'ssh_strict': False,
        'fast_cli': False,
    }

    # handling exceptions errors

    try:
        net_connect = ConnectHandler(**cisco)
    except NetMikoTimeoutException:
        f = open("Login_Issue.csv", "a")
        f.write(ip + "," + "Device Unreachable/SSH not Enabled")
        f.write("\n")
        f.close()
        continue
    except AuthenticationException:
        f = open("Login_Issue.csv", "a")
        f.write(ip + "," + "Authentication Failure")
        f.write("\n")
        f.close()
        continue
    except SSHException:
        f = open("Login_Issue.csv", "a")
        f.write(ip + "," + "SSH Not Enabled")
        f.write("\n")
        f.close()
        continue

    try:
        net_connect.enable()

    # handling exceptions errors
    except ValueError:
        f = open("Login_Issue.csv", "a")
        f.write(ip + "," + "Could be SSH Enable Password Issue")
        f.write("\n")
        f.close()
        continue

    # execute show version on router and save output to output object
    sh_ver_output = net_connect.send_command('show version')

    # finding hostname in output using regular expressions
    regex_hostname = re.compile(r'(\S+)\suptime')
    hostname = regex_hostname.findall(sh_ver_output)

    # finding uptime in output using regular expressions
    regex_uptime = re.compile(r'\S+\suptime\sis\s(.+)')
    uptime = regex_uptime.findall(sh_ver_output)
    uptime = str(uptime).replace(',', '').replace("'", "")
    uptime = str(uptime)[1:-1]

    # finding version in output using regular expressions
    regex_version = re.compile(r'Cisco\sIOS\sSoftware.+Version\s([^,]+)')
    version = regex_version.findall(sh_ver_output)

    # finding serial in output using regular expressions
    regex_serial = re.compile(r'Processor\sboard\sID\s(\S+)')
    serial = regex_serial.findall(sh_ver_output)

    # finding ios image in output using regular expressions
    regex_ios = re.compile(r'System\simage\sfile\sis\s"([^ "]+)')
    ios = regex_ios.findall(sh_ver_output)

    # finding model in output using regular expressions
    regex_model = re.compile(r'[Cc]isco\s(\S+).*memory.')
    model = regex_model.findall(sh_ver_output)

    # finding the router's memory using regular expressions
    regex_memory = re.search(r'with (.*?) bytes of memory', sh_ver_output).group(1)
    memory = regex_memory

    # append results to table [hostname,uptime,version,serial,ios,model,cmd]
    devices.append([ip, hostname[0], uptime, version[0], ios[0], serial[0], model[0], memory])

# print all results (for all routers) on screen
for i in devices:
    i = ", ".join(i)
    f = open("Inventory.csv", "a")
    f.write(i)
    f.write(" ")
    f.write("\n")
    f.close()
