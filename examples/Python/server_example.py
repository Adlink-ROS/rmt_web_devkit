#!/usr/bin/env python3
import rmt_py_wrapper
import json
import sys, getopt
import time
import psutil
import socket

def usage():
    print("Usage:")
    print("\t-g | --get_config")
    print("\t-s | --set_config")
    print("\t-n eth0 | --net-intf eth0")
    print("\t--send_file")
    print("\t--recv_file")
    print("Example:")
    print("\t./server_example.py -gs -n eth0")

def get_config(dev_list, dev_num):
    r"""
    Get current configuration and status from the given devices

    The following APIs are used to implement this function:
    - rmt_py_wrapper.rmt_server_get_info()
    """

    # Create config key string
    config_list = ["cpu", "ram", "hostname", "wifi"]
    config_key_str = ""
    for item in config_list:
        config_key_str += item + ';'

    # Get device info list
    id_list = rmt_py_wrapper.ulong_array(dev_num)
    for i in range(0, dev_num):
        id_list[i] = dev_list[i].deviceID
    info_num_ptr = rmt_py_wrapper.new_intptr()
    info_list = rmt_py_wrapper.data_info_list.frompointer(rmt_py_wrapper.rmt_server_get_info(id_list, dev_num, config_key_str, info_num_ptr))
    info_num = rmt_py_wrapper.intptr_value(info_num_ptr)
    rmt_py_wrapper.delete_intptr(info_num_ptr) # release info_num_ptr

    print("=== get config result ===")
    config_data = []
    for i in range(0, info_num):
        # Split the result string into dictionary data
        result_list = info_list[i].value_list.split(";")
        dict_data = {"deviceID": info_list[i].deviceID}
        print("deviceID=%d" % info_list[i].deviceID)
        for item in result_list:
            for key in config_list:
                if key in item:
                    dict_data[key] = item[len(key)+1:]
        # print(dict_data)
        config_data.append(dict_data)
    result = json.dumps(config_data, indent=4)
    print(result)

    # Free info_list
    rmt_py_wrapper.rmt_server_free_info(info_list.cast())

    return config_data

def set_diff_config():
    r"""
    Set different configurations or states to the given devices

    The following APIs are used to implement this function:
    - rmt_py_wrapper.rmt_server_set_info()
    """

    # Create data_info_array to set config
    dev_num = 2
    data_info_array = rmt_py_wrapper.new_data_info_array(dev_num)

    # Set for device 5566:
    data_info_element = rmt_py_wrapper.data_info()
    data_info_element.deviceID = 5566
    data_info_element.value_list = "hostname:rqi-1234;locate:on"
    dev_idx = 0
    rmt_py_wrapper.data_info_array_setitem(data_info_array, dev_idx, data_info_element)

    # Set for device 6166:
    data_info_element.deviceID = 6166
    data_info_element.value_list = "hostname:new_hostname;locate:on"
    dev_idx = 1
    rmt_py_wrapper.data_info_array_setitem(data_info_array, dev_idx, data_info_element)

    # Print what we want to set in data_info_array
    print("=== set diff config req ===")
    dev_idx = 0
    data_info_element = rmt_py_wrapper.data_info_array_getitem(data_info_array, dev_idx)
    print("deviceID=%d" % data_info_element.deviceID)
    print("value_list=%s" % data_info_element.value_list)
    dev_idx = 1
    data_info_element = rmt_py_wrapper.data_info_array_getitem(data_info_array, dev_idx)
    print("deviceID=%d" % data_info_element.deviceID)
    print("value_list=%s" % data_info_element.value_list)

    # Send data_info_array to RMT library
    info_num_ptr = rmt_py_wrapper.new_intptr()
    info_list = rmt_py_wrapper.data_info_list.frompointer(rmt_py_wrapper.rmt_server_set_info(data_info_array, dev_num, info_num_ptr))
    info_num = rmt_py_wrapper.intptr_value(info_num_ptr)
    rmt_py_wrapper.delete_intptr(info_num_ptr) # release info_num_ptr

    print("=== set diff config result ===")
    config_data = []
    for i in range(0, info_num):
        # Split the result string into dictionary data
        result_list = info_list[i].value_list.split(";")
        dict_data = {"deviceID": info_list[i].deviceID}
        # print(info_list[i].deviceID)
        # print(info_list[i].value_list)
        for item in result_list:
            key_value_pair = item.split(":")
            if len(key_value_pair) > 1:
                key = key_value_pair[0]
                value = key_value_pair[1]
                dict_data[key] = value
        # print(dict_data)
        config_data.append(dict_data)
    result = json.dumps(config_data, indent=4)
    print(result)

    # Free info_list
    rmt_py_wrapper.rmt_server_free_info(info_list.cast())

def set_same_config():
    r"""
    Set the same configuration or state to each given devices

    The following APIs are used to implement this function:
    - rmt_py_wrapper.rmt_server_set_info_with_same_value()
    """

    # Prepare mock data for setting config
    dev_num = 2
    id_list = rmt_py_wrapper.ulong_array(dev_num)
    id_list[0] = 5566
    id_list[1] = 5567
    config_str = "hostname:rqi-1234;locate:on"

    # Send data_info_array to RMT library
    info_num_ptr = rmt_py_wrapper.new_intptr()
    info_list = rmt_py_wrapper.data_info_list.frompointer(rmt_py_wrapper.rmt_server_set_info_with_same_value(id_list, dev_num, config_str, info_num_ptr))
    info_num = rmt_py_wrapper.intptr_value(info_num_ptr)
    rmt_py_wrapper.delete_intptr(info_num_ptr) # release info_num_ptr

    print("=== set same config result ===")
    config_data = []
    for i in range(0, info_num):
        # Split the result string into dictionary data
        result_list = info_list[i].value_list.split(";")
        dict_data = {"deviceID": info_list[i].deviceID}
        # print(info_list[i].deviceID)
        # print(info_list[i].value_list)
        for item in result_list:
            key_value_pair = item.split(":")
            if len(key_value_pair) > 1:
                key = key_value_pair[0]
                value = key_value_pair[1]
                dict_data[key] = value
        # print(dict_data)
        config_data.append(dict_data)
    result = json.dumps(config_data, indent=4)
    print(result)

    # Free info_list
    rmt_py_wrapper.rmt_server_free_info(info_list.cast())

def discover():
    r"""
    Discover all the available agents in the same network

    The following APIs are used to implement this function:
    - rmt_py_wrapper.rmt_server_create_device_list()
    """

    num_ptr = rmt_py_wrapper.new_intptr()
    dev_list = rmt_py_wrapper.device_info_list.frompointer(rmt_py_wrapper.rmt_server_create_device_list(num_ptr))
    num = rmt_py_wrapper.intptr_value(num_ptr)
    rmt_py_wrapper.delete_intptr(num_ptr) # release num_ptr

    # Put data in JSON format
    data = {"total": num, "items": []}
    items = []
    for i in range(0, num):
        item = {
            "ID": dev_list[i].deviceID,
            "Model": dev_list[i].model,
            "Host": dev_list[i].host,
            "IP": dev_list[i].ip,
            "MAC": dev_list[i].mac,
            "RMT_VERSION": dev_list[i].rmt_version,
            "Device_Info": dev_list[i].devinfo
        }
        items.append(item)

    print("=== discover result ===")
    data["items"] = items
    result = json.dumps(data, indent=4)
    print(result)
    return dev_list, num

def test_send_binary():
    r"""
    Send a binary file to the target device(s)

    The following APIs are used to implement this function:
    - rmt_py_wrapper.rmt_server_send_file()
    - rmt_py_wrapper.rmt_server_get_result()
    """

    print("=== test send binary ===")
    custom_callback = "custom_callback"
    filename = "my_testfile"
    bytes_buffer = b"a\0bc\r\ndef\tg" # convert to bytes
    dev_num = 1
    target_id = 6166
    id_list = rmt_py_wrapper.ulong_array(dev_num)
    id_list[0] = target_id

    agent_status = rmt_py_wrapper.rmt_server_send_file(id_list, dev_num, custom_callback, filename, bytes_buffer)
    print("send_file: agent_status=%d" % agent_status)

    agent_status, result, byte_array = rmt_py_wrapper.rmt_server_get_result(target_id)
    while agent_status == rmt_py_wrapper.STATUS_RUNNING:
        print("sleep for 1 second")
        time.sleep(1)
        agent_status, result, byte_array = rmt_py_wrapper.rmt_server_get_result(target_id)

    print("get_result: agent_status=%d" % agent_status)
    print("transfer_result=%d" % result)
    print(bytes(byte_array).decode("utf-8"))

def test_recv_binary():
    r"""
    Retrieve a binary file from a target device

    The following APIs are used to implement this function:
    - rmt_py_wrapper.rmt_server_recv_file()
    - rmt_py_wrapper.rmt_server_get_result()
    """

    print("=== test recv binary ===")
    target_id = 6166
    custom_callback = "custom_callback"
    filename = "my_testfile"

    agent_status = rmt_py_wrapper.rmt_server_recv_file(target_id, custom_callback, filename)
    print("recv_file: agent_status=%d" % agent_status)

    agent_status, result, byte_array = rmt_py_wrapper.rmt_server_get_result(target_id)
    while agent_status == rmt_py_wrapper.STATUS_RUNNING:
        print("sleep for 1 second")
        time.sleep(1)
        agent_status, result, byte_array = rmt_py_wrapper.rmt_server_get_result(target_id)

    print("get_result: agent_status=%d" % agent_status)
    print("transfer_result=%d" % result)
    print("file_len=%d" % len(byte_array))
    print("=== file content start ===")
    print(bytes(byte_array).decode("utf-8"))
    print("=== file content end ===")

def main(args):
    r"""
    Init and de-init RMT server library

    The following APIs are used to implement this function:
    - rmt_py_wrapper.rmt_server_version()
    - rmt_py_wrapper.rmt_server_configure()
    - rmt_py_wrapper.rmt_server_init()
    - rmt_py_wrapper.rmt_server_deinit()
    """

    def valid_interface(interface):
        interface_addrs = psutil.net_if_addrs().get(interface) or []
        return socket.AF_INET in [snicaddr.family for snicaddr in interface_addrs]

    try:
        opts, args = getopt.getopt(args, "hgsn:", ["help", "get_config", "set_config", "send_file", "recv_file", "net_intf="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    flag_get_config = False
    flag_set_config = False
    flag_send_file = False
    flag_recv_file = False
    my_interface = ""
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-g", "--get_config"):
            flag_get_config = True
        elif opt in ("-s", "--set_config"):
            flag_set_config = True
        elif opt in ("--send_file"):
            flag_send_file = True
        elif opt in ("--recv_file"):
            flag_recv_file = True
        elif opt in ("-n", "--net-intf"):
            my_interface = arg
            if not valid_interface(my_interface):
                print("Interface({}) is invalid or inactive.".format(my_interface))
                sys.exit(2)
        else:
            assert False, "unhandled option"

    # Get RMT_VERSION
    print("RMT_VERSION=%s" % rmt_py_wrapper.rmt_server_version())

    # Set network interface for DDS communication
    print("Use interface({}) for RMT server".format(my_interface))
    rmt_py_wrapper.rmt_server_configure(my_interface, 0)

    # Init RMT server
    rmt_py_wrapper.rmt_server_init()

    # Discovery devices
    dev_list, num = discover()

    # Get config
    if flag_get_config:
        get_config(dev_list, num)

    # Set config
    if flag_set_config:
        set_same_config()
        set_diff_config()

    # Send file
    if flag_send_file:
        test_send_binary()

    # Recv file
    if flag_recv_file:
        test_recv_binary()

    # Free & de-init
    rmt_py_wrapper.rmt_server_free_device_list(dev_list.cast())
    rmt_py_wrapper.rmt_server_deinit()

if __name__ == "__main__":
    args = sys.argv[1:]
    main(args)
