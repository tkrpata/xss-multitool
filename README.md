# XSS Multitool

A handy tool for dealing with XSS in CTFs (and maybe in real life?)

## Description

This tool provides helpful functions for Cross-Site Scripting (XSS) vulnerability testing and exploitation, particularly useful in Capture The Flag (CTF) competitions and security assessments.

## Features

- **XSS Payloads**: Generate and deliver various XSS payloads for different contexts
- **Serve and Catch**: Serve the XSS payload and catch the response in one place
- **Payload Encoding**: Encode payloads using different methods

## Installation

### Setup

1. Clone the repository:

```bash
git clone https://github.com/tkrpata/xss-multitool.git
cd xss-multitool
```

2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python xss-multitool.py [options]
```
### Options

General:
- `-h, --help`: show this help message and exit
- `-c, --callback`: Callback IP or hostname (specify by interface, IP, or hostname) (default: eth0)
- `--show-hints, --no-show-hints`: Show payload hints at startup (default: False)
- `--loglevel LOGLEVEL`: Log level (DEBUG, INFO, WARN, etc.) (default: INFO)

Server:
- `-l, --listen`: IP or interface to listen on (default: 0.0.0.0)
- `-p, --port`: Port to listen on (default: 8888)
- `--filename FILENAME`: Filename for payload (default: x.js)
- `--content-type CONTENTTYPE`: Content-Type header to send (default: text/plain)

Formatting:
- `--b64, --no-b64, --base64, --no-base64`: Base64 encode payload (default: True)
- `--min, --no-min`: JavaScript minimizer using jsmin (default: True)
- `--beautify, --no-beautify`: JavaScript beautifier on the local console using jsbeautify (default: False)

Payloads:
- `-t, --tiny, --no-tiny`: Use alternate minimal default payload (default: False)
- `-x, --exfil EXFIL`: Use alternate exfiltration payload (specify filename/URI to exfil) (default: None)
- `-f, --file FILE`: Load custom payload from file (default: None)
- `--payload PAYLOAD`: Load custom payload from argument (default: None)