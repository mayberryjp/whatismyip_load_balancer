import requests
import paho.mqtt.client as mqtt
import logging
import json
import re
import logging
import time

from const import CONST_WEBSITES,CONST_MQTT_HOST,CONST_MQTT_USERNAME,CONST_MQTT_PASSWORD,VERSION,CONST_SLEEP_INTERVAL

requests.packages.urllib3.util.connection.HAS_IPV6 = False

# Function to get payload from HTTP website
def get_http_payload(url):
    headers = {'User-Agent': 'curl/7.54'}
    response = requests.get(url,headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f'Failed to get payload from {url}')
        return None

def replace_periods(ip_address):
    return re.sub(r'\W', '_', ip_address)

def initialize():
    print("Initialize starting...")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    client.username_pw_set(CONST_MQTT_USERNAME,CONST_MQTT_PASSWORD)
    client.connect( CONST_MQTT_HOST, 1883)


    for website in CONST_WEBSITES:
        website_replace=replace_periods(website)
        mqtt_payload = {}
        mqtt_payload["name"]= f"whatismyip_{website_replace}"
        mqtt_payload["state_topic"]=f"homeassistant/sensor/whatismyip_{website_replace}/state"
        mqtt_payload["device_class"]=None
        mqtt_payload["unique_id"]=f"whatismyip_{website_replace}"

        device = {}
        device["identifiers"] = mqtt_payload["unique_id"]
        device["name"] = f"What Is My IP Response For {website}"

        mqtt_payload["device"] = device
        mqtt_payload = json.dumps(mqtt_payload)

        client.publish(f"homeassistant/sensor/whatismyip_{website_replace}/config", payload=mqtt_payload, qos=0, retain=True)

    client.disconnect()
    print("Initializing complete...")

# Function to publish payload to MQTT topic
def publish_to_mqtt():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    client.username_pw_set(CONST_MQTT_USERNAME,CONST_MQTT_PASSWORD)
    client.connect( CONST_MQTT_HOST, 1883)

    for website in CONST_WEBSITES:

        payload = get_http_payload(website)
        payload_strip = payload.strip()

        logger = logging.getLogger(__name__)
        logger.info(f"Website {website} reports {payload_strip}")
        print(f"Website {website} reports {payload_strip}")
        website_replace=replace_periods(website)

        client.publish(f"homeassistant/sensor/whatismyip_{website_replace}/state", payload=payload_strip, qos=0, retain=False)
 
    client.disconnect()

# Main process
if __name__ == '__main__':
    print(f"I am whatismyip_checker running {VERSION}")
    initialize()
    logger = logging.getLogger(__name__)

    while True:
        publish_to_mqtt()
        logger.info(f"Sleeping for {CONST_SLEEP_INTERVAL}")
        print(f"Sleeping for {CONST_SLEEP_INTERVAL}")
        time.sleep(CONST_SLEEP_INTERVAL)

