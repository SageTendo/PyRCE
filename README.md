# PyRCE: Remote Code Executor over TCP/IP

## Overview

> [!NOTE]
> This is still a work in progress.

PyRCE is a simple remote code execution tool using TCP sockets.
It consists a client-server model in which:

- The servers handles client (the target) connectivity
- Messages are sent/relayed betweeen clients and server
- Payloads can be injected and executed on target clients via the server

## Disclaimer
> [!WARNING]
> This project is intended for educational purposes only.
Unauthorized or malicious use is strictly prohibited. The user assumes full responsibility for any actions taken using this tool.
The creator, contributors, and maintainers of this project shall not be held liable for any damages, legal issues, or consequences resulting from its use. Use at your own risk.