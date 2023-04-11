#Name: xTLHostingWatchdog.py
#Author: x21

import configparser
import os
import shlex
import signal
import socket
import subprocess
import sys
import time

config = configparser.ConfigParser()
config.read('xTLHostingWatchdog.ini')

ServerIP = config.get('Watchdog.Config', 'ServerIP')
ServerPort = config.get('Watchdog.Config', 'ServerPort')
UnrealPath = config.get('Watchdog.Config', 'UnrealPath')
UnrealArguments = shlex.split(config.get('Watchdog.Config', 'UnrealArguments'))
SocketTimeout = config.getfloat('Watchdog.Tweaks', 'SocketTimeout')
StartupDelay = config.getfloat('Watchdog.Tweaks', 'StartupDelay')
CheckDelay = config.getfloat('Watchdog.Tweaks', 'CheckDelay')
MainLoopDelay = config.getfloat('Watchdog.Tweaks', 'MainLoopDelay')

fail_count = 0

process = subprocess.Popen([UnrealPath] + UnrealArguments)
time.sleep(StartupDelay)

def signal_handler(signum, frame):
	os.kill(process.pid, signal.SIGTERM)
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGHUP, signal_handler)
signal.signal(signal.SIGQUIT, signal_handler)

while True:
	time.sleep(MainLoopDelay)
	if process.poll() is None:
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
			sock.settimeout(SocketTimeout)
			try:
				sock.sendto(b'\\echo\\x21', (ServerIP, int(ServerPort)))
				data, _ = sock.recvfrom(1024)
				if b'\\queryid\\' not in data:
					raise Exception()
				fail_count = 0
				time.sleep(CheckDelay)
			except:
				fail_count += 1
				if fail_count < 3:
					time.sleep(CheckDelay)
				elif fail_count == 3:
					process.terminate()
					process = subprocess.Popen([UnrealPath] + UnrealArguments)
					time.sleep(StartupDelay)
					fail_count = 0
	else:
		process = subprocess.Popen([UnrealPath] + UnrealArguments)
		time.sleep(StartupDelay)