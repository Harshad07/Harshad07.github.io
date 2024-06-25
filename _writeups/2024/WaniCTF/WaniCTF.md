---
layout: writeup
category: WaniCTF
chall_description: 
points: 
solves: 
tags: 
date: 2024-06-21
comments: false
---


# Web

## Bad Worker

Javascript file named service-worker.js reveals that whenever we ask for the flag, a request goes to server for `DUMMY.txt` instead.
![Branching](/assets/CTFs/WaniCTF/bad-worker1.png)

Sending FLAG.txt to get the flag.
![Branching](/assets/CTFs/WaniCTF/bad-worker2.png)


Flag: `FLAG{pr0gr3ssiv3_w3b_4pp_1s_us3fu1}`



## POW

Javascript file sends a request to `/api/pow` with current number which keeps increasing with no progress.
After waiting for some time we finally get one increment it progress, which is at 2862152, let's see the response in burp.
![Branching](/assets/CTFs/WaniCTF/pow1.png)

Sending the same request results to server results in progress increment meaning server is not storing previously sent values so we can just send same number again.

I wrote the following script in Python to get teh flag

```py
import httpx

client = httpx.Client(http2=True)
url = "https://web-pow-lz56g6.wanictf.org/" 

while True:
    payload = '[ ' + '"2862152",'*100000 + '"2862152"]'
    response = client.post(url+"api/pow", data=payload )
    
    print(response.text )
    if (response.text).startswith("FLAG"):
        print(response.text )
        exit()

```

```shell
┌──(kali㉿kali)-[~/…/CTF/WaniCTF/web/pow]
└─$ python3 solve.py
progress: 100001 / 1000000
progress: 200002 / 1000000
progress: 300003 / 1000000
progress: 400004 / 1000000
progress: 500005 / 1000000
progress: 600006 / 1000000
progress: 700007 / 1000000
progress: 800008 / 1000000
progress: 900009 / 1000000
FLAG{N0nCE_reusE_i$_FUn}
FLAG{N0nCE_reusE_i$_FUn}

```

FLAG: `FLAG{N0nCE_reusE_i$_FUn}`


# Reverse 


## Home


Loading the binary in Ghidra to check the dissassembly.
![Branching](/assets/CTFs/WaniCTF/home1.png)


We need to have Service somewhere in our full path. It also checks for PTRACE which is used by GDB. We can easily bypass that in GDB by placing breakpoint where the condition check happens for PTRACE detection and change the value of RAX to 0.
![Branching](/assets/CTFs/WaniCTF/home2.png)


Put breakpoint anywhere at the end of `constructFlag` function and dump stack values to get the flag.

![Branching](/assets/CTFs/WaniCTF/home3.png)


Flag: `FLAG{How_did_you_get_here_4VKzTLibQmPaBZY4}`


