---
layout: writeup
category: picoCTF
chall_description: 
points: 400
solves: 1167
tags: web picoCTF
date: 2024-06-19
comments: true
misc: true
---

### Java Script analysis:

The initial index page consists of javascript code used to decrypt the image file coming from the server in decimal. We need a key of length 16 to decrypt the image.

```js

var bytes = [];
$.get("bytes", function(resp) {
    bytes = Array.from(resp.split(" "), x => Number(x));
});

function assemble_png(u_in){
    var LEN = 16;
    var key = "0000000000000000";
    var shifter;
    if(u_in.length == LEN){
        key = u_in;
    }
    var result = [];
    for(var i = 0; i < LEN; i++){
        shifter = key.charCodeAt(i) - 48;
        for(var j = 0; j < (bytes.length / LEN); j ++){
            result[(j * LEN) + i] = bytes[(((j + shifter) * LEN) % bytes.length) + i]
        }
    }
    while(result[result.length-1] == 0){
        result = result.slice(0,result.length-1);
    }
    document.getElementById("Area").src = "data:image/png;base64," + btoa(String.fromCharCode.apply(null, new Uint8Array(result)));
    return false;
}

```



Let's analyze the logic part of the decryption.

```js
for(var i = 0; i < LEN; i++){
    shifter = key.charCodeAt(i) - 48;
    for(var j = 0; j < (bytes.length / LEN); j ++){
        result[(j * LEN) + i] = bytes[(((j + shifter) * LEN) % bytes.length) + i]
    }
}
```


If you notice the following snippet, it takes 16-byte blocks from the image data and performs shifting operations based on key. The blocks are created as follows.
 
![Branching](/assets/CTFs/picoCTF/java-script-kiddie1.png)

Bruteforcing the key of size 16 is not feasible but we know that it's a PNG file and the first 16 bytes of a PNG file stay the same for every image. So we only have to brute force the first 16 bytes. 


Initial 16 bytes of any PNG file are the following `8950 4e47 0d0a 1a0a 0000 000d 4948 4452`.
```shell
┌──(kali㉿kali)-[~/Downloads]
└─$ xxd download.png 
00000000: 8950 4e47 0d0a 1a0a 0000 000d 4948 4452  .PNG........IHDR
00000010: 0000 00d8 0000 00e9 0803 0000 0071 d809  .............q..
00000020: d700 0000 7e50 4c54 45ff ffff 0000 000a  ....~PLTE.......
00000030: 0a0a 8f8f 8fa7 a7a7 cbcb cbd7 d7d7 bcbc  ................
00000040: bccf cfcf e0e0 e092 9292 6464 649a 9a9a  ..........ddd...

```



### Undestading decryption code for first 16 bytes block: 
* Iterate from ascii values 48 to 57 which are 0 to 9 in decimal
* Check if the `result[0]=png_bytes[0]`
* Repeat the process for all 16 bytes

Feel free to check out the full decryption code. [Github Link](https://github.com/Harshad07/CTF-Solutions/blob/main/Misc/picoCTF/Java-Script-Kiddie/solve.js)
```js
var png_hex = "137,80,78,71,13,10,26,10,0,0,0,13,73,72,68,82"; // first 16 bytes of png in decimal
var png_bytes = [];
png_bytes = Array.from(png_hex.split(","), x => Number(x)); 
var u_in = "0000000000000000"; 
var key = ""
for(var j = 0; j < 16 ; j++){
    for(var i = 48 ; i <= 57 ; i++){
        var payload = key + String.fromCharCode(i) + u_in.slice(1,u_in.length-key.length);  
        var result = assemble_png_16Bytes(payload); 
        if (result[j] == png_bytes[j]){ // Checking bytes
            console.log("Position: " + j + " Char: " + String.fromCharCode(i) + " Res:" + result[j]);
            key = key + String.fromCharCode(i);
            break;
        }
    }
}
console.log("Key: "+key); 
```


In the function `assemble_png_16Bytes` only change I made was in the inner `j` loop it only runs one time to save time as we only care about the first 16 byes.

```shell
┌──(kali㉿kali)-[~/practice/picoCTF/web_exploitation/java_script_kiddie]
└─$ node solve.js
Position: 0 Char: 6 Res:137
Position: 1 Char: 6 Res:80
Position: 2 Char: 9 Res:78
Position: 3 Char: 6 Res:71
Position: 4 Char: 7 Res:13
Position: 5 Char: 0 Res:10
Position: 6 Char: 5 Res:26
Position: 7 Char: 9 Res:10
Position: 8 Char: 6 Res:0
Position: 9 Char: 7 Res:0
Position: 10 Char: 8 Res:0
Position: 11 Char: 3 Res:13
Position: 12 Char: 5 Res:73
Position: 13 Char: 4 Res:72
Position: 14 Char: 6 Res:68
Position: 15 Char: 3 Res:82
Key: 6696705967835463

```


We get a QR code after submitting the code.
![Branching](/assets/CTFs/picoCTF/java-script-kiddie1.png)

 
And we got the flag!
![Branching](/assets/CTFs/picoCTF/java-script-kiddie3.png)




### References
[JS Kiddie writeup by @radekk](https://medium.com/@radekk/picoctf-2019-writeup-for-js-kiddie-7af4f0a20838)


