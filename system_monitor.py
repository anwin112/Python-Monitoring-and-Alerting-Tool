import psutil
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import os
from dotenv import load_dotenv
import socket

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

#Configuration
CPU_THRESHOLD = 80  # in percentage
MEMORY_THRESHOLD = 80  # in percentage
DISK_THRESHOLD = 90  # in percentage
ALERT_EMAIL = os.getenv("ALERT_EMAIL")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("APP_PASSWORD")

if not SMTP_PASSWORD:
    print("Warning: APP_PASSWORD environment variable not set. Email alerts will not work.")



def send_alert(resource, usage):
    if not SMTP_PASSWORD:
        print(f"Alert: {resource} usage is at {usage}% (Email not configured)")
        return
    
    try:
        subject = f"Alert : {resource} usage is at {usage}%"
        body = f"{resource} warning: Current usage is at {usage}% as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.Please check your system"
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = ALERT_EMAIL

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, ALERT_EMAIL, msg.as_string())
        print(f"Alert sent: {resource} usage at {usage}%")
    except Exception as e:
        print(f"Failed to send alert for {resource}: {str(e)}")
    
def check_thresholds():
    cpu_usage = psutil.cpu_percent(interval=1)
    if cpu_usage > CPU_THRESHOLD:
        send_alert("CPU", cpu_usage)
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    if memory_usage > MEMORY_THRESHOLD:
        send_alert("Memory", memory_usage)
    
    for partition in psutil.disk_partitions():
        if partition.fstype !='':
            disk_usage = psutil.disk_usage(partition.mountpoint).percent
            if disk_usage > DISK_THRESHOLD:
                send_alert(f"Disk ({partition.mountpoint})", disk_usage)
def main():
    hostname  = socket.gethostname()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
    print(f"System Monitor Report - {current_time}")
    print(f"Hostname: {hostname}")
    print(f"System Uptime: {uptime}")
    print(f"CPU Usage: {psutil.cpu_percent(interval=1)}%")
    print(f"Memory usage: {psutil.virtual_memory().percent}%")
    print(f"Disk usage:")
    for partition in psutil.disk_partitions():
        if partition.fstype != '':
            usage = psutil.disk_usage(partition.mountpoint).percent
            print(f"  {partition.mountpoint}: {usage}%")
check_thresholds()

if __name__ == "__main__":
    main()