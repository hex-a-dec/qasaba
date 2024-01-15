<p align="center"> ██████╗  █████╗ ███████╗ █████╗ ██████╗  █████╗
    █╔═══██╗██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔══██╗ 
    ██║   ██║███████║███████╗███████║██████╔╝███████║
    ██║▄▄ ██║██╔══██║╚════██║██╔══██║██╔══██╗██╔══██║
    ╚██████╔╝██║  ██║███████║██║  ██║██████╔╝██║  ██║ 
    ╚══▀▀═╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝</p>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Go](https://img.shields.io/badge/go-1.18-red.svg)
![Release](https://img.shields.io/badge/release-1.0-yellow.svg)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

In Amazigh regions, a qasaba (Arabic: قَـصَـبَـة) is a fortified residence, often built of mudbrick. A safe place in a realm of sand and loneliness.

## Overview

Qasaba is a minimalist command-and-control (C2) project that combines cross-platform agents developed in Golang and a multi-client server made in Python. Communications between the server and agents is carried out using TLS. Thus, The Python server comes with an agent generation feature for Windows and Linux. 

### Philosophy

When starting my OSEP prep, I had the feeling that creating a basic C2 framework, that is not heavily signatured by AV engines, would have given me more options during the final exam. It's obvious that Qasaba doesn't aim to replace a proven C2 framework, such as Meterpreter or Covenant. Instead, Qasaba should be seen as an extra card in my deck as well as a side-project.

I'm not a very experienced and talented developper, thus I wanted to take advantage of this opportunity to practice in Python as well as learn a new compiled language, such as Golang. I was traumatized by a previous experience with C#, so I did not feel well to delve once again into this language.

Consequently, I did not want to over-engineer Qasaba for two main reasons: 
- **keep code very simple** helps to grow it organically, as new features would later become vital. I chose Golang and Python, because writting a C2 is sufficently complicated as it is. 
- write **limited functions to reduce the agent's footprint**. It helps during the process of bypassing AV's engines. Most of the time, basic commands execution and file upload functions mixed with "living off the land" techniques are enough to reach the set goals.
- I had only few weeks to spend to this the project. Every hour should count.

Regarding pentest engagements, my philosophy is always the same and can be summed-up in a very simple moto. The less you expose, the easier it is to stay under the radar. 
Qasaba has been developed with this philosophy in mind.

### Functionalities

In few words, the server offers the following functionalities:
- **multi-client handling**
- **basic sessions information for every agent**, such as last seen, current user or hostname
- **communication over rawTLS** through a self-signed certificate. The content of every socket is base64-encoded.
- **cross-platform payload** generation, including x64 and X32 Windows executable, x64 linux ELF format and x64 Windows shared libraries (DLL)

The agents have limited capabilities such as:
- **command execution**
- **change directory (cd) function**
- **file upload**
- a basic SOCKS5 may be added in the future

## Installation

### Requirements:
- Go
- Python3
- mingw-w64
- rlwrap (optional)

### Setup:
On a debian-like machine:
```bash
cd /opt/qasaba
# Setting a virtualenv
sudo virtualenv qasaba-venv 
source qasaba-venv/bin/activate
# Installing required package
pip3 install prettytable colorama
# generate self-signed certificate
cd utils/key
openssl req -newkey rsa:4096  -x509  -sha512  -days 365 -nodes -out cert.pem -keyout cert.key
```

## Usage

The project is divded into three components: 
- a server in Python (`main.py`)
- a directory (`agents/`) that contains generated agents and templates (`agents/template/`) used during the payload generation. In this directory, you will find templates that you can use to generate more verbose agents for debugging or learning purposes.
- an `utils/` directory that contains the self-signed certificate used for TLS communications and a yara rule that can help you to detect default Qasaba's agents if you need to house clean after an exercice or do some hunting. I'm not a Yara specialist, feel free to contribute.

The following snapshots show a basic usage which includes running a listener, building an agent then interacting with it:

![qas3](https://github.com/hex-a-dec/qasaba/assets/152536937/345bcb69-a670-491f-bdae-9e2e75b1e564)

![qas 2](https://github.com/hex-a-dec/qasaba/assets/152536937/211a2237-cb31-469b-a2a6-c36b07ffdf84)

You can find more help using `:help` from the `c2 >` main menu.

## Credits
A special thanks goes to :
- [0xRick and his "Building a Basic C2](https://0xrick.github.io/misc/c2/). in my opinion, his blog post grasps very well the fundamentals of writing a C2
- [Joe Helle. His tutorial "Python3 Command and Control How to Guide"](https://medium.themayor.tech/python3-command-and-control-how-to-guide-1d539618b777) was a vital contribution to me, because it helps me to create a working back-bone from wich I could build Qasaba.
- [Djnn and his "What I learned writing a loader in Golang"](https://djnn.sh/what-i-learned-writing-a-loader-in-golang/) blog post which was inspiring when it comes to not over-engineer to much things
