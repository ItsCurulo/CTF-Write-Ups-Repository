# 🔨 Hammer Time - TryHackMe Write-up (The "I'm In" Edition)
**By Curulo** (a.k.a. The One Who Knocks)

**Difficulty:** Medium (but felt like a rollercoaster 🎢)
**Description:** Join me on this chaotic journey to bypass authentication and get that sweet, sweet RCE. 🕶️

---

## 1. 🕵️‍♂️ Enumeration: "Knock Knock"

### 📡 Port Scan
First things first, let's see who's home. I fired up `nmap` and waited... and waited... ⏳

```bash
nmap -sC -sV -oN report hammer.thm
```

**Results:**
- `22/tcp`: SSH (Open) - The front door is locked. 🔒
- `1337/tcp`: HTTP (Open) - Oho! A back door on a fancy port? Let's peek. 👀

### 🌐 Web Enumeration
I visited `http://hammer.thm:1337` and was greeted by a login page. Classic. But I have trust issues, so I ran a directory fuzz to see what they're hiding under the rug. 🧹

#### 📂 Directory Fuzzing

```bash
gobuster dir -u http://hammer.thm:1337 -w /usr/share/wordlists/dirb/common.txt -t 50
```

**Findings:**
- `/index.php` - The lobby.
- `/phpmyadmin` - Oh, hello there! 👋 (But I don't have the keys yet).
- `/hmr_logs` - **BINGO!** 🎉 Someone left the diary open! (Found this by reading developer notes in the source code like a stalker).

#### 📝 Source Code Shenanigans
I checked the source of `index.php` and saw a dev note:
`<!-- Dev Note: Directory naming convention must be hmr_DIRECTORY_NAME -->`
Thanks, Mr. Developer! You just gave me the map! 🗺️

Then I looked at `reset_password.php`. It had a countdown timer. ⏲️ It was screaming "RACE CONDITION" or "BRUTE FORCE ME".

#### 📜 Reading their Diary (`/hmr_logs/error.log`)
I poked around `/hmr_logs/error.log` and saw someone failing to log in (probably me in a past life).
`[authz_core:error] ... user tester@hammer.thm: authentication failure ...`

**Target Acquired:** `tester@hammer.thm` 🎯

## 2. 💥 Exploitation: "Hacker Man Mode"

### 🔓 Authentication Bypass
I tried to reset the password for `tester@hammer.thm`. The site asked for a 4-digit code.
"Only 4 digits?" I laughed. "I eat 4 digits for breakfast!" 🥣

But wait... **Rate Limiting**. 🛑 The fun police arrived.
"Rate limit exceeded," it said.
"Hold my beer," I said. 🍺

**The Trick:** I spoofed my IP using the `X-Forwarded-For` header. Take that!

#### ⚔️ The Attack Plan
1.  Ask for a reset code.
2.  Brute force the code (0000-9999).
3.  Every few tries, change my "identity" (Session ID) so the server thinks I'm a new person. 🥸
4.  Profit. 💸

I wrote a script `brute_code.py` to do the heavy lifting because manual labor is for muggles.

### 💻 Dashboard Access (I'm In!)
The script found the code! I reset the password and logged in.
**Flag 1:** `THM{AuthBypass3D}` 🚩 (Nom nom nom)

But I wanted MORE. I wanted to run commands. 😈
I saw a command input, but it was just echoing stuff back. Boring.

Then I saw the **JWT Token**. `eyJ...`
I decoded it. It had a `kid` (Key ID) pointing to `/var/www/mykey.key`.
"Hmm," I thought. "What if I tell it to look at... another file?" 🤔

### 💉 JWT Key Confusion (The betrayal)
I used the command line to `ls` and found `188ade1.key` right there in the open.
I read it: `56058354efb3daa97ebab00fabd7a7d7`

**The Master Plan:**
1.  Make a fake badge (JWT).
2.  Tell the server the "key" is in `188ade1.key`.
3.  Sign it with the content I just stole.
4.  Tell the server I am `admin`. 🤴

I ran my `forge_jwt.py` script and boom! I was admin.

## 3. 🚀 Privilege Escalation: "Look at me, I am the Captain now"

### 👤 User Flag
First, I stabilized my shell so I wouldn't lose it like my patience.
`cat /home/ubuntu/flag.txt`
**Flag 2:** `THM{RUNANYCOMMAND1337}` 🚩

### 🛡️ Escalating to Root
I looked around for SUID binaries, running services, or loose change in the sofa.
(Insert standard priv-esc montage here).
Files found, exploits run, root shell obtained! 💪

**Root Flag:** `root.txt` 🚩 (The Holy Grail)

---

## 💰 Loot & Answers (The cheat sheet)

**1. What is the flag value after logging in to the dashboard?**
   - **Flag:** `THM{AuthBypass3D}`

**2. What is the content of the file /home/ubuntu/flag.txt?**
   - **Flag:** `THM{RUNANYCOMMAND1337}`

And that's how we hammer the Hammer! 🔨💥
