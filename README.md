# Tiny SSH Honeypot
 
A minimal SSH honeypot in Python. It pretends to be an SSH server, rejects every
login, and logs each attempt (IP, username, password, client version) as JSON.
 
## Setup
 
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
 
## Configuration
 
Edit `.env`:
 
| Variable        | Default                          | Description                    |
|-----------------|----------------------------------|--------------------------------|
| `HONEYPOT_HOST` | `0.0.0.0`                        | Interface to listen on         |
| `HONEYPOT_PORT` | `2222`                           | Port to listen on              |
| `LOG_FILE`      | `honeypot.jsonl`                 | Where attempts are saved       |
| `SSH_BANNER`    | `SSH-2.0-OpenSSH_8.9p1 Ubuntu-3` | Fake SSH version shown to bots |
 
## Run
 
```bash
python honeypot.py
```
 
Test it (any password will be rejected):
 
```bash
ssh -p 2222 test@127.0.0.1
```
 
## Logs
 
One JSON object per line in `honeypot.jsonl`:
 
```json
{"ip": "127.0.0.1", "user": "test", "password": "abc123", "client": "SSH-2.0-OpenSSH_9.6", "time": "2026-11-26T14:02:11"}
```
 
## Safety
 
- Run on a throwaway VPS or isolated VM, never on your home network.
- Move your real SSH to another port first, then redirect 22 to 2222:
  `iptables -t nat -A PREROUTING -p tcp --dport 22 -j REDIRECT --to-port 2222`
- Run as an unprivileged user, ideally in Docker.
- This honeypot never accepts logins. Keep it that way.
- Don't commit `.env` or the log file (they are in `.gitignore`).
 