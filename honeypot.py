import os, socket, threading, json, time
import paramiko
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("HONEYPOT_HOST", "0.0.0.0")
PORT = int(os.getenv("HONEYPOT_PORT", "2222"))
LOG_FILE = os.getenv("LOG_FILE", "honeypot.jsonl")
BANNER = os.getenv("SSH_BANNER", "SSH-2.0-OpenSSH_8.9p1 Ubuntu-3")

HOST_KEY = paramiko.RSAKey.generate(2048)
lock = threading.Lock()

def log(event):
    event["time"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    with lock, open(LOG_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")

class FakeSSH(paramiko.ServerInterface):
    def __init__(self, ip, transport_ref):
        self.ip = ip
        self.tr = transport_ref

    def check_auth_password(self, username, password):
        log({"ip": self.ip, "user": username, "password": password,
             "client": getattr(self.tr[0], "remote_version", "?")})
        return paramiko.AUTH_FAILED  # never let anyone in

    def get_allowed_auths(self, username):
        return "password"

def handle(client, addr):
    try:
        t = paramiko.Transport(client)
        t.local_version = BANNER
        t.add_server_key(HOST_KEY)
        t.start_server(server=FakeSSH(addr[0], [t]))
        t.accept(20)
    except Exception:
        pass
    finally:
        client.close()

sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((HOST, PORT))
sock.listen(100)
print(f"Honeypot listening on {HOST}:{PORT}")

while True:
    c, a = sock.accept()
    threading.Thread(target=handle, args=(c, a), daemon=True).start()
