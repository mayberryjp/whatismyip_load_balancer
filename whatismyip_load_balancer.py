import requests
import paho.mqtt.client as mqtt
import logging
import json
import re
import logging
import time
import os
from random import randrange
import datetime

from const import CONST_WEBSITES_V4,VERSION,CONST_SLEEP_INTERVAL, IS_CONTAINER, CONST_WEBSITES_V6

WEBSITES=[]

def on_connect(client, userdata, flags, rc):
    if rc != 0:
        print(f"Failed to connect with result code {rc}")
        # Handle the connection failure
    else:
        print("Connected successfully")

if (IS_CONTAINER):
    CONST_MQTT_HOST=os.getenv("MQTT_HOST","earthquake.832-5.jp")
    CONST_MQTT_PASSWORD=os.getenv("MQTT_PASSWORD","earthquake")
    CONST_MQTT_USERNAME=os.getenv("MQTT_USERNAME","japan")

VERSION_STRING = os.getenv("VERSION","v4")

if (VERSION_STRING == "v4"):
    WEBSITES=CONST_WEBSITES_V4
    requests.packages.urllib3.util.connection.HAS_IPV6 = False
else:
    WEBSITES=CONST_WEBSITES_V6
    requests.packages.urllib3.util.connection.HAS_IPV6 = True
    VERSION_STRING="v6"

# Function to get payload from HTTP website
def get_http_payload(url):
    headers = {'User-Agent': 'curl/7.54'}
    response = requests.get(url,headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f'Failed to get payload from {url}')
        return "Unknown"

def replace_periods(ip_address):
    return re.sub(r'\W', '_', ip_address)

class WhatIsMyIpSensor:
    def __init__(self, name):
        name_replace=replace_periods(name)
        self.name = f"whatismyip{VERSION_STRING}_{name_replace}"
        self.device_class = None
        self.state_topic = f"homeassistant/sensor/whatismyip{VERSION_STRING}_{name_replace}/state"
        self.unique_id = f"whatismyip{VERSION_STRING}_{name_replace}"
        self.device = {
            "identifiers": [f"whatismyip{VERSION_STRING}_{name_replace}"],
            "name": f"What Is My IP{VERSION_STRING} Response For {name}"
        }

    def to_json(self):
        return {
            "name": self.name,
            "device_class": self.device_class,
            "state_topic": self.state_topic,
            "unique_id": self.unique_id,
            "device": self.device
        }

def initialize():
    logger = logging.getLogger(__name__)
    logger.info(f"Initialization starting...")
    print("Initialization starting...")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.username_pw_set(CONST_MQTT_USERNAME,CONST_MQTT_PASSWORD)
    client.connect( CONST_MQTT_HOST, 1883)

    for website in WEBSITES:

        website_replace=replace_periods(website)
        whatismyip_sensor=WhatIsMyIpSensor(website)
        # Convert dictionary to JSON string
        serialized_message = json.dumps(whatismyip_sensor.to_json())
        print(f"Sending sensor -> {serialized_message}")
        logger.info(f"Sending sensor -> {serialized_message}")
        client.publish(f"homeassistant/sensor/whatismyip{VERSION_STRING}_{website_replace}/config", payload=serialized_message, qos=0, retain=True)
 
    client.disconnect()
    logger.info(f"Initialization complete...")
    print("Initialization complete...")

# Function to publish payload to MQTT topic
def ping_and_publish():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.username_pw_set(CONST_MQTT_USERNAME,CONST_MQTT_PASSWORD)
    client.connect( CONST_MQTT_HOST, 1883)
    logger = logging.getLogger(__name__)

    sites = {}

    count=0

    logger.info(f"Checking...",end="")
    print(f"Checking...",end="")


    for website in WEBSITES:
        logger.info(f"{count}..,",end="")
        print(f"{count}..",end="")

        payload = "Unknown"

        try: 
           payload = get_http_payload(website)
        except:
            logger.info(f"{website} failed, skipping")
            print(f"{website} failed, skipping")

        payload_strip = payload.strip()

        # logger.info(f"Website {website} reports {payload_strip}")
        # print(f"Website {website} reports {payload_strip}")
        website_replace=replace_periods(website)
        sites[payload_strip] = sites.get(payload_strip, 0) + 1
        count=count+1

        client.publish(f"homeassistant/sensor/whatismyip{VERSION_STRING}_{website_replace}/state", payload=payload_strip, qos=0, retain=False)
    
    client.disconnect()

    logger.info(f"")
    print(f"")

    logger.info(f"I iterated over {count} sites and saw {len(sites)} unique IP addresses")
    print(f"I iterated over {count} sites and saw {len(sites)} unique IP addresses")
    
    for site in sites.keys():
        logger.info(f"IP {site} was seen {sites[site]} times")
        print(f"IP {site} was seen {sites[site]} times")

# Main process
if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.info(f"I am whatismyip_load_balancer running version {VERSION}")
    print(f"I am whatismyip_load_balancer running version {VERSION}")
    initialize()

    while True:

        ping_and_publish()
        sleep_interval = randrange(CONST_SLEEP_INTERVAL,CONST_SLEEP_INTERVAL*2)
        logger.info(f"It is {datetime.datetime.now()} .. I am sleeping for {sleep_interval}")
        print(f"It is {datetime.datetime.now()} ... I am sleeping for {sleep_interval}")
        time.sleep(sleep_interval)
