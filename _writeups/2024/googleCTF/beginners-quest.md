---
layout: writeup
category: googleCTF
chall_description: 
points: 
solves: 
tags: 
date: 2024-06-21
comments: false
---


# Googlectf beginner’s quest

## 0000

### challenge 0

Caesar cipher with key 13
Flag: `FLAG{rotate_that_alphabet}`

### Challenge 1 

![Branching](/assets/CTFs/googleCTF/beginners-quest/0000chal1.png)

Vinegre cipher with key `CAESAR`
Flag: `FLAG{get_viggy_with_it}`


### Challenge2

Used this site to know decrypt the cipher. [boxentriq](https://www.boxentriq.com/code-breaking/cryptogram)

![Branching](/assets/CTFs/googleCTF/beginners-quest/0000chal2.png)

Flag: `FLAG{NOW_IVE_LEARNED_MY_ABCS}`


## 1836

### Challenge 0

```
..-. .-. --- --/-.   .   .--/-.-- --- .-. -.-/.. .   ..   -   .. ../..- ... .-/-   . ./.-.. --- -. -.. --- -./..-   -.   ..   -   .   -../-.- .. -. --. -.. --- --/. ..   .   ..-.   ..-   .   ...   -/- ---/.   .-..   -   . ..   .-   .. .   -/..-. .-.. .- --./{-   . ..   ....-   -.   ---   ....-   -   â¸º   ....-   -.   -   ..   .. .}/--- -./. .   . ..   -..   .   . ../--- ..-./...   .   -.   -..   .   . ../--. --- --- --. .-.. ./.. .   -   .-.
```

This morce code contained both American and International morse code.

International morse decode
```
FROM NEW YORK IEITII USA TEE LONDON UNITED KINGDOM EIEFUEST TO ELTEIAIET FLAG {TEI4NO4Tâ¸º4NTIIE} ON EEEIDEEI OF SENDEEI GOOGLE IETR
```

American morse decode
```
\# NEW # CITY # TO # UNITED # REQUEST # EXTRACT # TR4N54T4NTIC # ORDER # SENDER # CTF
```

Final Morse
```
FROM NEW YORK CITY USA TEE=TO LONDON UNITED KINGDOM REQUEST TO EXTRACT FLAG {TEI4NO4Tâ¸º4NTIIE} ON ORDER OF SENDER GOOGLE CTF
```

Supposed Flag: `FLAG{TR4N54T4NTIC}` 

After trying many combinations I wasnt able to get the correct flag so skipped this one.



## 1943

### Challenge 0


We are given base64 encoded key.

```shell
                                                                                          
┌──(kali㉿kali)-[~/practice/CTF/googleCTF/24]
└─$ echo VGhlIFZlbm9uYSBwcm9qZWN0IHdhcyBhIFVuaXRlZCBTdGF0ZXMgY291bnRlcmludGVsbGlnZW5jZSBwcm9ncmFtIGluaXRpYXRlZCBkdXJpbmcgV29ybGQgV2FyIElJLg== | base64 -d   
The Venona project was a United States counterintelligence program initiated during World War II.                                                                                          

```

Using this text as key we get the flag

![Branching](/assets/CTFs/googleCTF/beginners-quest/1943chal0.png)


FLAG: `CTF{Ace_of_Spies}`



