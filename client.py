
#!/usr/bin/python
# -*- coding: utf-8 -*-

from tkinter import *
import threading
import random
import socket
import time
import sys


server = ("192.168.0.208",8888)
client_type = 'test-client'
client_name = 'Client-1'
client_port = 8889
host = 'localhost'
mainFrame = None
shutdown = False
join = False
rT = None
T = None
s = None


def cmd(window, v, command):
	command = command.get()
	c = v.get()
	if c == 0:
		s.sendto(('cmd ' + command).encode("utf-8"), server)
	elif c == 1:
		s.sendto(('sendToVKCMD ' + command).encode("utf-8"), server)
	elif c == 2:
		s.sendto(('sendToTGCMD ' + command).encode("utf-8"), server)
	window.destroy()


def cmd_window():

	cmdWindow = Tk()

	v = IntVar()

	cmdWindow.title('Client')
	cmdWindow.resizable(0, 0)

	label = Label(cmdWindow, text = 'Input command', fg='black')
	command = Entry(cmdWindow, width = 30)

	radio1 = Radiobutton(cmdWindow, text = 'Send result to client', variable = v, value = 0, command = lambda : v.set(0))
	radio2 = Radiobutton(cmdWindow, text = 'Send result to VK', variable = v, value = 1, command = lambda : v.set(1))
	radio3 = Radiobutton(cmdWindow, text = 'Send result to Telegram', variable = v, value = 2, command = lambda : v.set(2))
	radio1.select()
	button = Button(cmdWindow, text = 'Execute', command = lambda : cmd(cmdWindow, v, command))

	label.pack()
	command.pack()
	radio1.pack()
	radio2.pack()
	radio3.pack()
	button.pack()

	cmdWindow.mainloop()


def sendClients(tp):
	if tp == 'vk':
		s.sendto('sendToVKclients'.encode("utf-8"), server)
	else:
		s.sendto('sendToTGclients'.encode("utf-8"), server)


def sendToVK(window, message):
	message = message.get()
	window.destroy()
	s.sendto(('sendToVK ' + message).encode("utf-8"), server)


def sendToTG(window, message):
	message = message.get()
	window.destroy()
	s.sendto(('sendToTG ' + message).encode("utf-8"), server)


def sendToClient(window, message, port):
	message = message.get()
	port = int(port.get())
	window.destroy()

	s.sendto(('sendTo ' + str(port) + ' ' + message).encode("utf-8"), server)


def sendToClientWindow():
	sendToClientWindow = Tk()

	sendToClientWindow.title('Client')

	sendToClientWindow.resizable(0, 0)

	label1 = Label(sendToClientWindow, text = 'Input message', fg='black')
	message = Entry(sendToClientWindow, width = 20)

	label2 = Label(sendToClientWindow, text = 'Input port', fg='black')
	port = Entry(sendToClientWindow, width = 5)
	
	button = Button(sendToClientWindow, text= 'Send', command = lambda : sendToClient(sendToClientWindow, message, port))

	label1.config(font=('Arial', 14, 'bold'))
	label2.config(font=('Arial', 14, 'bold'))
	message.config(font=('Arial', 14, 'bold'))
	port.config(font=('Arial', 14, 'bold'))
	button.config(font=('Arial', 14, 'bold'))

	label1.grid(column = 0, row = 0)
	message.grid(column = 1, row = 0, columnspan = 2)

	label2.grid(column = 0, row = 1)
	port.grid(column = 1, row = 1)
	button.grid(column = 2, row = 1)

	sendToClientWindow.mainloop()


def send(tp):
	sendWindow = Tk()

	sendWindow.title('Client')

	sendWindow.resizable(0, 0)

	label = Label(sendWindow, text = 'Input message', fg='black')
	message = Entry(sendWindow, width = 30)
	if tp == 'vk':
		button = Button(sendWindow, text= 'Send to VK', command = lambda : sendToVK(sendWindow, message))
	else:
		button = Button(sendWindow, text= 'Send to Telegram', command = lambda : sendToTG(sendWindow, message))

	label.config(font=('Arial', 14, 'bold'))
	message.config(font=('Arial', 14, 'bold'))
	button.config(font=('Arial', 14, 'bold'))

	label.pack()
	message.pack()
	button.pack()

	sendWindow.mainloop()


def close_connection():
	global mainFrame
	global shutdown

	mainFrame.destroy()
	s.sendto(('ClientDisconnect:' + client_name + ':' + client_type).encode("utf-8"),server)
	rT.join()
	shutdown = True
	s.close()


def connect(window, ip, port):
	global client_port
	global server
	global rT
	global s

	ip = ip.get()
	port = int(port.get())

	server = (ip, port)

	window.destroy()

	set_client_ip()
	s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	client_port = random.randint(8000, 9000)
	s.bind((host, client_port))
	s.setblocking(0)

	s.sendto(('ClientConnect:' + client_name + ':' + client_type).encode('utf-8'), server)

	rT = threading.Thread(target = receving, args = ("RecvThread",s))
	rT.start()

	mainWindow()


def connect_window():
	connectWindow = Tk()

	connectWindow.title('Client')

	connectWindow.resizable(0, 0)

	servIP_label = Label(connectWindow, text = 'Input server IP: ', fg='black')
	servIP = Entry(connectWindow, width = 15)

	servPort_label = Label(connectWindow, text = 'Input server port: ', fg='black')
	servPort = Entry(connectWindow, width = 15)

	connectButton = Button(connectWindow, text= 'Connect', command = lambda : connect(connectWindow, servIP, servPort))

	servIP_label.grid(column = 0, row = 0)
	servIP.grid(column = 1, row = 0)

	servPort_label.grid(column = 0, row = 1)
	servPort.grid(column = 1, row = 1)

	connectButton.grid(column = 0, columnspan = 2, row = 2)

	connectWindow.mainloop()


def mainWindow():
	global mainFrame
	global T

	mainFrame = Tk()

	mainFrame.title('Client')

	mainFrame.resizable(0, 0)
	info = 'Server: ' + server[0] + ':' + str(server[1]) + '\n' + 'Client: ' + host + ':' + str(client_port)
	infolabel = Label(mainFrame, text = info, fg='black')

	label1 = Label(mainFrame, text = 'Functions', fg='black')
	label2 = Label(mainFrame, text = 'Server log', fg='black')

	clientsButton = Button(mainFrame, width = 30, text = 'Clients list', command = lambda: s.sendto('clients'.encode("utf-8"), server))

	sendToVKbutton = Button(mainFrame, width = 30, text = 'Send message to VK', command = lambda : send('vk'))
	sendToTGbutton = Button(mainFrame, width = 30, text = 'Send message to Telegram', command = lambda : send('tg'))

	sendToVKclientsButton = Button(mainFrame, width = 30, text = 'Send clients list to VK', command = lambda : sendClients('vk'))
	sendToTGclientsButton = Button(mainFrame, width = 30, text = 'Send clients list to Telegram', command = lambda : sendClients('tg'))

	cmdButton = Button(mainFrame, width = 30, text = 'Execute command', command = lambda: cmd_window())

	screenButton = Button(mainFrame, width = 30, text = 'Send screenshot to VK', command = lambda: s.sendto('screen'.encode("utf-8"), server))

	sendToClientButton = Button(mainFrame, width = 30, text = 'Send message to client', command = lambda: sendToClientWindow())
	clearButton = Button(mainFrame, width = 30, text = 'Clear server log', command = lambda: T.delete(1.0, END))

	T = Text(mainFrame, height = 40, width = 60)

	label1.config(font=('Arial', 14, 'bold'))
	label2.config(font=('Arial', 14, 'bold'))

	infolabel.grid(column = 0, row = 0)

	label1.grid(column = 0, row = 1)
	label2.grid(column = 1, row = 0)
	T.grid(column = 1, row = 1, rowspan = 100)

	clientsButton.grid(column = 0, row = 2)

	sendToVKbutton.grid(column = 0, row = 3)
	sendToTGbutton.grid(column = 0, row = 4)

	sendToVKclientsButton.grid(column = 0, row = 5)
	sendToTGclientsButton.grid(column = 0, row = 6)
	cmdButton.grid(column = 0, row = 7)
	screenButton.grid(column = 0, row = 8)
	sendToClientButton.grid(column = 0, row = 9)
	clearButton.grid(column = 0, row = 10)

	mainFrame.protocol("WM_DELETE_WINDOW", close_connection)

	mainFrame.mainloop()


def set_client_ip():
	global host

	getipsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	getipsocket.connect(("8.8.8.8", 80))
	host = getipsocket.getsockname()[0]
	getipsocket.close()


def receving(name, sock):
	global shutdown
	global join
	global T

	while not shutdown:
		try:
			while True:
				data, addr = sock.recvfrom(1024)
				decrypt = data.decode("utf-8")
				if decrypt == 'stopclient':
					shutdown = True
					break
				else:
					T.insert(END, '\n' + decrypt)
				time.sleep(0.2)
		except:
			pass


if __name__ == '__main__':
	connect_window()