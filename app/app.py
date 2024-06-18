import config

from flask import Flask, request
from multiprocessing import Lock
from multiprocessing.managers import AcquirerProxy, BaseManager, DictProxy
import subprocess
from enum import Enum
import appdirs, argparse
from tradfricoap.config import get_config, host_config, ConfigNotFoundError
import traceback

CONFIGFILE = "{0}/gateway.json".format(appdirs.user_config_dir(appname="tradfri"))
CONF = get_config(CONFIGFILE).configuation

import tradfricoap.device

ikea_devices, plugs, blinds, groups, others, batteries = tradfricoap.device.get_sorted_devices(groups=True)

supergroup = next(filter(lambda x: x.Name == "SuperGroup", groups), None)
assert supergroup is not None, "SuperGroup not found"



class LockState(Enum):
    LOCKED = '0'
    OPEN = '1'
    INBETWEEN = '2'


def get_shared_state(host, port, key):
    shared_dict = {}
    shared_lock = Lock()
    manager = BaseManager((host, port), key)
    manager.register("get_dict", lambda: shared_dict, DictProxy)
    manager.register("get_lock", lambda: shared_lock, AcquirerProxy)
    try:
        manager.get_server()
        manager.start()
    except OSError:  # Address already in use
        manager.connect()
    return manager.get_dict(), manager.get_lock()

def kelder_open():
    subprocess.Popen(["cvlc", "--play-and-exit", "--no-loop", "bootup.m4a"])
    supergroup.State = 1

def kelder_close():
    subprocess.Popen(["cvlc", "--play-and-exit", "--no-loop", "shutdown.m4a"])
    supergroup.State = 0


app = Flask(__name__)

shared_dict, shared_lock = get_shared_state("127.0.0.1", 35791, b'not secret')

shared_dict["last_state"] = 'unknown'

@app.route("/kelderapi/doorkeeper", methods=["POST"])
def doorkeeper():
    if request.headers.get("Token") != config.doorkeeper_token:
        return abort(401)
    content = request.get_json()
    with shared_lock:
        if content['why'] == 'state':
            new_lock_state = content['val']
            if new_lock_state != shared_dict['last_state']:
                try:
                    if new_lock_state == LockState.OPEN.value:
                        kelder_open()
                    elif new_lock_state == LockState.LOCKED.value:
                        kelder_close()
                except:
                    return f"kelderapi crash\n{traceback.format_exc()}", 500
            shared_dict['last_state'] = new_lock_state
    return "OK"
