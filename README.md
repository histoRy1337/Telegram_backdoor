# Telegram_backdoor

This is a Windows-only backdoor that you can control through a Telegram bot.

What's on the menu ? 
- Reverse Shell
- Screenshots
- Keylogger
- File transfert
- Webcam photo capture
- Microphone sound recording
- Purge
- And more coming..!

The commands are listed in the /man command.

How to make it work ?
Copy the .py file, the credentials.txt file (and ffmpeg.exe if you want to record the microphone) in any directory.


How to create the Telegram bot ? 
- Contact BotFather on Telegram, generate your bot and your token. 
- Call the getUpdates API page : https://api.telegram.org/bot{TOKEN}/getUpdates and get your chat_id.
- Fill the credentials.txt file with the datas.
- The backdoor is ready be used.


Disclaimer : This backdoor is not meant to infect anybody that does not consent. I use it for my personnal monitoring needs, which are my workplace and my home. Windows defender blocks it anyways if you try to use it as an executable.
