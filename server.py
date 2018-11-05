
from datetime import date
import pandas as pd
import subprocess
import pyautogui
import datetime
import requests
import hashlib
import socket
import json
import time
import os
import vk


proxies = dict(http='YOUR PROXIES', https='YOUR PROXIES')
vk_token = ''
tg_token = ''
pushover_user = ''
pushover_token = ''
pushover_url = 'https://api.pushover.net/1/messages.json'
sendToTGURL = 'https://api.telegram.org/bot' + tg_token + '/sendMessage?chat_id=&text='
session = vk.Session(access_token = vk_token)
stdian_vk_id = 216301387
vkapi = vk.API(session)
host = '192.168.0.208'
clients = []
port = 8888


def sendToTG(text):
	url = sendToTGURL + text
	try:
		resp = requests.get(url, proxies = proxies)
	except:
		pass


def sendPush(text):
	r = requests.post(pushover_url, data = {
		"token": pushover_token,
		"user": pushover_user,
		"message": text
	})


def sendToVK(text):
	try:
		vkapi.messages.send(v = '5.85', peer_id = stdian_vk_id, message = text)
	except:
		pass


def server():
	global clients
	today = date.today()
	datatime = time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime())
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind((host, port))
	print('[ SERVER START ]' + '=' + '['+ datatime + ']')
	quit = False
	while not quit:
		try:
			data, addr = s.recvfrom(1024)
			decrypt = data.decode("utf-8")

			if decrypt[:14] == 'ClientConnect:':
				d = decrypt[14:]
				d = d.split(':')
				if [addr, d[0], d[1]] not in clients:
					clients.append([addr, d[0], d[1]])
				print('Connected: ' + d[0] + '\nIP: ' + addr[0] + ' Port: ' + str(addr[1]))
			elif decrypt[:17] == 'ClientDisconnect:':
				d = decrypt[17:]
				d = d.split(':')
				try:
					clients.remove([addr, d[0], d[1]])
				except:
					pass
				s.sendto('stopclient'.encode("utf-8"), addr)
				print('Disconnected: ' + d[0] + '\nIP: ' + addr[0] + ' Port: ' + str(addr[1]))
			elif decrypt == 'clients':
				c1 = []
				c2 = []
				c3 = []

				for client in clients:
					c1.append(client[0])
					c2.append(client[1])
					c3.append(client[2])

				df = pd.DataFrame({
					'Client Name': c2,
					'Client Type': c3
				}, index = c1)
				
				s.sendto(('\n' + str(df)).encode("utf-8"), addr)
			elif decrypt == 'screen':
				pic = pyautogui.screenshot()
				pic.save('screen.png')
				data = vkapi.photos.getMessagesUploadServer(peer_id = stdian_vk_id, v = '5.85')
				url = data['upload_url']
				img = {'photo': ('screen.png', open(r'screen.png', 'rb'))}
				r = requests.post(url, files = img)
				r = json.loads(r.text)
				server = r['server']
				photo = r['photo']
				hash = r['hash']
				photo_id = vkapi.photos.saveMessagesPhoto(server = server, photo = photo, hash = hash, v = '5.85')
				photo_id = photo_id[0]['id']
				vkapi.messages.send(v = '5.85', peer_id = stdian_vk_id, attachment = 'photo' + str(stdian_vk_id) + '_' + str(photo_id))
			elif decrypt == 'sendToTGclients':
				st = ''

				for client in clients:
					st = st + client[0][0] + ':' + str(client[0][1]) + '  ' + client[1] + '  ' + str(client[2]) + '\n'

				sendToTG(st)
			elif decrypt == 'sendToVKclients':
				st = ''

				for client in clients:
					st = st + client[0][0] + ':' + str(client[0][1]) + '  ' + client[1] + '  ' + str(client[2]) + '\n'

				sendToVK(st)
			elif decrypt[:9] == 'sendToTG ':
				d = decrypt[9:]
				sendToTG(d)
			elif decrypt[:9] == 'sendToVK ':
				d = decrypt[9:]
				sendToVK(d)
			elif decrypt[:7] == 'sendTo ':
				d = decrypt[7:]
				d = d.split(' ')
				for client in clients:
					if int(d[0]) == client[0][1]:
						reply = ''
						for i in d[1:]:
							reply = reply + i + ' '
						s.sendto(('\nmessage from ' + str(addr)).encode("utf-8"), client[0])
						s.sendto(reply.encode("utf-8"), client[0])
			elif decrypt[:4] == 'cmd ':
				decrypt = decrypt[4:]
				try:
					r = subprocess.check_output(decrypt, shell=True)
					try:
						r = '\n' + r.decode('cp866')
					except:
						r = '\n'.join(map(chr, r))
				except:
					r = 'Error!'
				s.sendto(r.encode("utf-8"), addr)
			elif decrypt[:12] == 'sendToTGCMD ':
				decrypt = decrypt[12:]
				try:
					r = subprocess.check_output(decrypt, shell=True)
					try:
						r = r.decode('cp866')
					except:
						r = "".join(map(chr, r))
				except:
					r = 'Error!'
				sendToTG(r)
			elif decrypt[:12] == 'sendToVKCMD ':
				decrypt = decrypt[12:]
				try:
					r = subprocess.check_output(decrypt, shell=True)
					try:
						r = r.decode('cp866')
					except:
						r = "".join(map(chr, r))
				except:
					r = 'Error!'
				sendToVK(r)
			elif decrypt[:9] == 'sendPush ':
				decrypt = decrypt[9:]
				if decrypt == 'clients':
					st = ''
					for client in clients:
						st = st + client[0][0] + ':' + str(client[0][1]) + '  ' + client[1] + '  ' + str(client[2]) + '\n'
					sendPush(st)
				else:
					sendPush(decrypt)
			elif decrypt[:12] == 'sendPushCMD ':
				decrypt = decrypt[12:]
				try:
					r = subprocess.check_output(decrypt, shell=True)
					try:
						r = r.decode('cp866')
					except:
						r = "".join(map(chr, r))
				except:
					r = 'Error!'
				sendPush(r)
			elif decrypt == 'shutdown':
				print(clients)
				for client in clients:
					s.sendto('stopclient'.encode("utf-8"), addr)
			elif decrypt == 'stopserver':
				quit = True
				exit()
			elif decrypt == 'restart':
				quit = True
				server()
			else:
				print(decrypt)
					
		except:
			print("\n[ SERVER STOPPED ]")	
			quit = True
			exit()
	s.close()


if __name__ == '__main__':
	server()