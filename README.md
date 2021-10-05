# RebeLykos
RebeLykos is modern, asynchronous, multiplayer and multiserver AWS attacking tool powered by Python 3.

# Setup
```console
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

```console
$ python rebelykos.py client wss://<username>:<teamserver_password>@<teamserver_ip>:5000
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
