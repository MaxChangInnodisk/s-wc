# -*- coding: UTF-8 -*-

import os
import json
import glob
import datetime
import configparser
import importlib.util
import shutil
import numpy as np
import ctypes
import logging as log
import platform

def check_dir(trg_dir: str) -> str:
    """if directory is not exists then create it """
    if not os.path.exists(trg_dir):
        os.makedirs(trg_dir)
    return trg_dir

def clean_dir(trg_dir: str) -> str:
    """if directory is not exists then create it """
    if os.path.exists(trg_dir):
        shutil.rmtree(trg_dir)
    return trg_dir


def read_ini(config_file: str) -> configparser.ConfigParser:
    if not os.path.exists(config_file):
        raise FileNotFoundError("Can not find config file. ({})".format(config_file))
    config = configparser.ConfigParser()
    # config.read(config_file, encoding='UTF-8')
    config.read(config_file, encoding='utf-8-sig')
    # print(config["output"]["history_dir"])
    return config


def write_ini(config: configparser.ConfigParser, config_file: str):
    with open(config_file, 'w') as configfile:    # save
        config.write(configfile)
    if not os.path.exists(config_file):
        raise RuntimeError("Write config failed.")

def read_json(json_file: str):
    if not os.path.exists(json_file):
        raise FileNotFoundError("Could not find json file: {}".format(json_file))
    with open(json_file, "r") as f:
        data = json.load(f)
    return data

def write_json(output:dict, json_file:str):
    with open(json_file, "w") as jsonfile:
        json.dump(output, jsonfile, indent=4, cls=NpEncoder)

def copy_file(src: str, dst: str):
    return shutil.copy(src, dst)

def find_folder_with_key(keyword: str, path: str= "./"): 
    input_folders = glob.glob(os.path.join(path, f"*{keyword}*"))
    assert len(input_folders)==1, f"Except only one input folder here but got {len(input_folders)}"

    input_folder = input_folders[0]
    if not os.path.isdir(input_folder):
        raise TypeError("Support input must be a folder: {}".format(input_folder))
    
    return input_folder

def get_data(keyword: str, path: str= "./") -> list: 
    input_folder = find_folder_with_key(keyword, path)
    data = glob.glob(f"{input_folder}/*")
    assert len(data)>0, "The data folder does not have any data !!!"
    return data

def get_timestamp():
    n = datetime.datetime.now()
    return f"{str(n.year)[-2:]}{n.month:02}{n.day:02}{n.hour:02}{n.minute:02}"

def get_label(label_path: str):
    ret = []
    with open(label_path, "r") as f:
        for line in f.readlines():
            line = line.replace('\n')
            ret.append(line)
    return ret

def import_module(module_name: str, module_path: str):
        
        # Check
        if not os.path.exists(module_path):
            raise FileNotFoundError("Moduel file not exists")
        # Load
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        # creates a new module based on spec
        module = importlib.util.module_from_spec(spec)
        # executes the module in its own namespace
        # when a module is imported or reloaded.
        spec.loader.exec_module(module)
        return module

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

def is_admin():
    # ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", "/k", None, 1)
    # try:
    #     return ctypes.windll.shell32.IsUserAnAdmin()
    # except:
    #     return False
    assert ctypes.windll.shell32.IsUserAnAdmin(), "Ensure using Administrator to execute the classifier.exe"
    
def is_win():
    # return platform.system()
    assert platform.system() == "Windows", "Ensure the platform is Windows"

def check_env():
    [ func() for func in (is_admin, is_win) ]

def get_exec_cmd(exec_key: str, config: dict) -> str:
    
    exec_info = config[exec_key]
    assert exec_info != None, f"Unexpect exec file key ... ({exec_key})"

    cmd = f"{exec_info['exec']} {exec_info['args']}"
    log.debug('Get execute command: {}'.format(cmd))
    return cmd

def check_status(service:str, config:dict) -> int:
    return int(config[service]["enable"])