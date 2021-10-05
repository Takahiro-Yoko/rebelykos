# RebeLykos
RebeLykos is modern, asynchronous, multiplayer and multiserver AWS attacking tool powered by Python 3 and [SILENTTRINITY](https://github.com/byt3bl33d3r/SILENTTRINITY) which I stole awesome code.

# Setup
```bash
$ git clone https://github.com/Takahiro-Yoko/rebelykos.git
$ cd rebelykos

$ apt-get install python3-venv -y (if required)

$ python3 -m venv rebelykos
$ source rebelykos/bin/activate

$ pip install -r requirements.txt
```

# Basic Usage
Start a Teamserver, the default port is 5000:
```console
$ python rebelykos.py teamserver <teamserver_ip> <teamserver_password>
```
Connect to a teamserver:

<b>Note the wss:// (two s's) in the URL which indicates an encrypted websocket connection (TLS), without this all traffic from the client to the teamserver will be in cleartext!</b>

```console
$ python rebelykos.py client wss://<username>:<teamserver_password>@<teamserver_ip>:5000
```
Alternatively, run rebelykos.py without any arguments and connect to a teamserver manually using the CLI menu:
```console
$ python rebelykos.py client
[0] RL ≫ teamservers
[0] RL (teamservers) ≫ connect -h
        Connect to the specified teamserver(s)

        Usage: connect [-h] <URL>...

        Arguments:
            URL teamserver url(s)

[0] RL (teamservers) ≫ connect wss://username:strongpassword@127.0.0.1:5000
```

# Notes
RebeLykos is currently supported in Linux.

# Involuntary Contributors
[SILENTTRINITY](https://github.com/byt3bl33d3r/SILENTTRINITY)<br />
[Rhino Security Labs](https://rhinosecuritylabs.com)<br />
[AWS pwn](https://github.com/dagrz/aws_pwn)<br />
[Sparc Flow](https://github.com/HackLikeAPornstar)<br />
[Miguel](https://menendezjaume.com/post/gpg-encrypt-terraform-secrets/)<br />
[weirdAAL](https://github.com/carnal0wnage/weirdAAL)<br />
Yushi Sato for teaching me programming.<br />
