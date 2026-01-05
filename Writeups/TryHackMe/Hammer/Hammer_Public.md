# Hammer🔨 - TryHackMe Write-up
**By Curulo**

**Difficulty:** Medium 
**Description:** A walkthrough on how I bypassed authentication mechanisms on the Hammer machine and achieved RCE.

---

## 1. Enumeration

### Port Scan
I kicked things off with a simple `nmap` scan to identify open ports and services.

```bash
nmap -sC -sV -oN report hammer.thm
```

**Results:**
```
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.11 (Ubuntu Linux; protocol 2.0)
1337/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: Login
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

### Web Enumeration
Since port **1337** was open, I headed over to `http://hammer.thm:1337` to check it out. While checking the site, I ran a directory fuzz to see if anything was hiding in plain sight.

#### Directory Fuzzing

```bash
gobuster dir -u http://hammer.thm:1337 -w /usr/share/wordlists/dirb/common.txt -t 50
# Or using feroxbuster
# feroxbuster -u http://hammer.thm:1337 -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

**Findings:**
- `/index.php` (Status: 200) - **Main Login Page** (Contains "Forgot your password?" link).
- `/phpmyadmin` (Status: 301) - **Accessible** (Standard phpMyAdmin login).
- `/vendor` (Status: 301)
- `/javascript` (Status: 301)

#### Digging into the Source
I checked the source code of `index.php` and found a developer note that gave away their naming convention:
```html
<!-- Dev Note: Directory naming convention must be hmr_DIRECTORY_NAME -->
```
This was a solid lead—I just needed to look for directories starting with `hmr_`.

I also analyzed `reset_password.php`. It used JavaScript for a countdown and mentioned entering a code. The script updated a hidden field `id="s"` with the countdown value and redirected to `logout.php` when time ran out. This setup smelled like it might be vulnerable to a race condition or rate-limit bypass.

**What I found:**
- `/hmr_css`, `/hmr_images`, `/hmr_js` (Just standard assets).
- **`/hmr_logs`** (Status: 301) - **Bingo!** This directory likely contains server logs.

#### Login Page Analysis
- **URL:** `http://hammer.thm:1337/login.php`
- **Reset Password Behavior:**
    - When I tried `test@test.com`, it immediately said "Invalid email address!".
    - This meant I could enumerate users. If I found a valid email, the error message would likely be different.

#### Log Analysis (`/hmr_logs/error.log`)
Browsing the logs, I spotted a valid email address:
`[authz_core:error] ... user tester@hammer.thm: authentication failure ...`

- **Valid User:** `tester@hammer.thm`

## 2. Exploitation

### Authentication Bypass
I decided to target the "Forgot Password" functionality using the user I found.

1.  **Input:** `tester@hammer.thm` in the reset form.
2.  **Expected Outcome:** A prompt for a 4-digit code.
3.  **Vulnerability:** The way the countdown worked suggested I might be able to guess the code if I could bypass rate limiting.
4.  **Obstacle:** I hit a "Rate limit exceeded" error pretty quickly.
    - **Bypass:** I used the `X-Forwarded-For` header to spoof my IP address and get around the block.

#### Attack Plan
- **Step 1:** Submit `tester@hammer.thm` to start the reset process.
- **Step 2:** The application limited attempts per session, but the 4-digit code didn't change between sessions.
- **Step 3:** I could brute-force the code (0000-9999). I figured I'd need to rotate my session ID (get a new PHPSESSID) every ~7 attempts to reset the rate limit counter.
- **Step 4:** To find the correct code, I'd monitor the response length—a success page should be a different size than a failure page.

I wrote a python script called `brute_code.py` to automate this session rotation.

**Usage:**
```bash
python3 brute_code.py -t <TARGET_IP>
```

The script iterates through the codes, rotating the session cookie every few requests, and prints the valid code once found.

### Gaining Dashboard Access
With the correct code, I successfully reset the password for `tester@hammer.thm`.

### Dashboard Access & Initial Flag
Logging in dropped me into a dashboard.
**Flag:** `THM{?}`

The dashboard had a command execution interface. I took a peek at the HTML source and found a JWT token handling authorization:
```javascript
var jwtToken = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImtpZCI6Ii92YXIvd3d3L215a2V5LmtleSJ9...';
```
Decoded Header:
```json
{
  "typ": "JWT",
  "alg": "HS256",
  "kid": "/var/www/mykey.key"
}
```
Decoded Payload:
```json
{
  "iss": "http://hammer.thm",
  "aud": "http://hammer.thm",
  "iat": 1767520053,
  "exp": 1767523653,
  "data": {
    "user_id": 1,
    "email": "tester@hammer.thm",
    "role": "user"
  }
}
```

### Exploit: JWT Key Confusion / Path Traversal
The `kid` (Key ID) parameter in the header pointed to a file path: `/var/www/mykey.key`. This strongly suggested the server was reading the content of that file to verify the HMAC signature.

**Discovery:**
I used the command injection interface (`ls`) to look around and found `188ade1.key` sitting in the web root.

**Found Key:**
Reading the content of `188ade1.key` gave me the secret: `REDACTED_KEY`

**Note:** The app kept logging me out (`tester@hammer.thm`) because of a client-side check (`checkTrailUserCookie`). It was annoying, but didn't stop the exploit.

**Attack Vector:**
1.  **Read/Download Key:** I grabbed the key from `/188ade1.key`.
2.  **Forge Token:**
    -   I created a new JWT.
    -   Set `kid` to point to the key I found: `188ade1.key`.
    -   Set `role` to `admin`.
    -   Signed it using the `REDACTED_KEY` as the secret.

#### Automation
I whipped up a script, `forge_jwt.py`, to generate the token for me.

**Usage:**
```bash
python3 forge_jwt.py --key "REDACTED_KEY"
```
3.  **Execute:** With the forged token, I could execute commands as admin.

#### Alternative: Burp Suite
Instead of using a script, I could just intercept the request in Burp Suite and manually replace the `Authorization` header with the forged token.
Command executed: `cat /home/ubuntu/flag.txt`

## 3. Privilege Escalation

### Getting the User Flag
After getting command execution, the first thing I did was stabilize my shell. With a proper shell, I could sniff around easily. I grabbed the user flag from `/home/ubuntu/flag.txt`.

**Flag:** `THM{?}`

### Escalating to Root
Now for the big prize: root.

I started my standard enumeration routine—checking `sudo -l`, SUID binaries, capabilities, and running `linpeas` to see if anything screams "vulnerable". The goal here is to find a misconfiguration or a vulnerable service running as root to pivot.

**Flag:** `root.txt`

---

## Loot & Answers

Here are the answers to the room's questions based on my findings.

### Flags
**1. What is the flag value after logging in to the dashboard?**
   - **Flag:** `THM{?}`

**2. What is the content of the file /home/ubuntu/flag.txt?**
   - **Flag:** `THM{?}`

### Other Finds
- Credentials found: `user:pass`
- Interesting files: `/path/to/file`
