#!/usr/bin/env python3

import json
import time
import paho.mqtt.client as mqtt
import aprs
import tarantool
import traceback
from classes import LocationFrame
import pymysql.cursors
from configparser import ConfigParser
import io

config = ConfigParser()

with open("/opt/APRSProxy/settings.ini") as f:
	config.read_file(f)

# constants
mqtt_channel = config['mqtt']['channel']
mqtt_master = config['mqtt']['master']
aprs_call = config['aprs']['call']
aprs_filter = config['aprs']['filter'].encode()
aprs_destination = config['aprs']['destination']
aprs_con = False
tnt_con = False
sqlcon = pymysql.connect(host=config['mysql']['dbhost'], user=config['mysql']['dbuser'], password=config['mysql']['dbpass'], db=config['mysql']['dbname'], charset='utf8', cursorclass=pymysql.cursors.DictCursor)

# functions
def aprs_passcode(callsign):
	"""
	Takes a CALLSIGN and returns passcode
	"""
	callsign = str(callsign)

	callsign = callsign.split('-')[0].upper()

	code = 0x73e2
	for i, char in enumerate(callsign):
		code ^= ord(char) << (8 if not i % 2 else 0)

	return bytes(str(code & 0x7fff), 'UTF-8')

def on_disconnect(client, userdata, rc):
	print("MQTT Disconnected, result code: "+str(rc))

def on_connect(client, userdata, flags, rc):
	print("MQTT Connected, result code "+str(rc))
	client.subscribe(mqtt_channel, 1)

def tntCallsign(msid):
	res = tnt_con.space('GlobalProfiles').select(msid)
	ssid = res[0][8] if res else ""
	suffix = ("-%s" % ssid) if ssid else ""
	return (res[0][7] + suffix, res[0][10], res[0][9]) if res else ()

def on_message(client, userdata, message):
	global aprs_con
	global aprs_filter
	global aprs_call
	message.payload = json.loads(message.payload)
	try:
		sign = tntCallsign(message.payload['SourceID'])
		frame = LocationFrame()
		frame.source = sign[0] if sign[0] and sign[0] is not "0" else message.payload['SourceID']
		frame.destination = aprs_destination
		frame.latitude = aprs.dec2dm_lat(message.payload['Latitude'])
		frame.longitude = aprs.dec2dm_lng(message.payload['Longitude'])
		frame.course = message.payload['Course']
		frame.speed = message.payload['Speed']
		frame.altitude = message.payload['Altitude']
		frame.symboltable = sign[2][0]
		frame.symbolcode = sign[2][1] if len(sign[2]) > 1 else sign[2][0]
		frame.comment = sign[1]
		frame.make_frame()
	except Exception as inst:
		print("[-] Exception raised",flush=True)
		print(type(inst),flush=True)
		print(inst.args,flush=True)
		print(inst,flush=True)
		print(traceback.format_exc(),flush=True)
		print("[-] Exception end",flush=True)
	try:
		aprs_con.send(frame.text)
	except (ConnectionResetError, BrokenPipeError, TimeoutError):
		print("APRS connection reset")
		aprs_con = aprs.TCP(user=aprs_call, password=aprs_passcode(aprs_call), aprs_filter=aprs_filter)
		aprs_con.start()
		aprs_con.send(frame.text)
	except Exception as inst:
		print("APRS send error unhandled")
		traceback.print_exc()
	try:
		sql = "INSERT INTO Positions (`ID`,`DMRID`,`Master`,`Latitude`,`Longitude`,`Speed`,`Course`,`Altitude`) VALUES (null,%s,%s,%s,%s,%s,%s,%s)"
		altitude = message.payload['Altitude']
		altitude = altitude if altitude and altitude.isdigit() else 0
		vals = (message.payload['SourceID'],mqtt_master,message.payload['Latitude'],message.payload['Longitude'],message.payload['Speed'],message.payload['Course'],altitude)
		with sqlcon.cursor() as cursor:
			cursor.execute(sql, vals)
		sqlcon.commit()
	except Exception as inst:
		print("SQL log error unhandled")
		traceback.print_exc()

# main loop
if __name__ == "__main__":
	aprs_con = aprs.TCP(user=aprs_call, password=aprs_passcode(aprs_call), aprs_filter=aprs_filter)
	print("APRS connect start")
	aprs_con.start()

	tnt_con = tarantool.connect(config['tarantool']['dbhost'], config['tarantool']['dbport'], config['tarantool']['dbuser'], config['tarantool']['dbpass'])

	mqtt_con = mqtt.Client()
	mqtt_con.on_connect = on_connect
	mqtt_con.on_message = on_message
	mqtt_con.on_disconnect = on_disconnect

	mqtt_con.connect_async('127.0.0.1', 1883)
	# blocking call
	print("MQTT loop start")
	mqtt_con.loop_forever()
	print("MQTT ended")
