
import os
import requests

if "PLAYER_EVENT" not in os.environ or os.environ["PLAYER_EVENT"] != "play":
    exit(0)

try:
    # track_id = os.environ['TRACK_ID']
    # res = requests.get(f'https://api.spotify.com/v1/tracks/{track_id}')
    # json = res.json()
    requests.post('http://10.0.0.171:8080/spotify', json={"track_id": str(os.environ['TRACK_ID'])})
except Exception:
    pass

from tradfricoap.config import get_config, host_config, ConfigNotFoundError
import appdirs

CONFIGFILE = "{0}/gateway.json".format(appdirs.user_config_dir(appname="tradfri"))
CONF = get_config(CONFIGFILE).configuation

import tradfricoap.device

ikea_devices, plugs, blinds, groups, others, batteries = tradfricoap.device.get_sorted_devices(groups=True)

#for thing in [ikea_devices, plugs, blinds, groups, others, batteries]:
#    print()
#    for dev in thing:
#        print(dev.Description)

light = next(filter(lambda x: x.Name == "server", ikea_devices), None)
assert light is not None, "Light not found"

import time

light.State = 1
time.sleep(0.5)
light.State = 0
time.sleep(0.5)
light.State = 1

#assert ikea_devices is not None, "Light not found"

#import time

#_ = list([light.State = 1 for light in ikea_devices])
#time.sleep(0.5)
#_ = list([light.State = 0 for light in ikea_devices])
#time.sleep(0.5)
#_ = list([light.State = 1 for light in ikea_devices])

