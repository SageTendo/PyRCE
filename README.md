# PyRCE: Remote Code Executor over TCP/IP

## Overview

PyRCE is a simple remote code execution tool using TCP sockets.
It consists a client-server model in which:

- The servers handles client (the target) connectivity
- Messages are sent/relayed betweeen clients and server
- Payloads can be injected and executed on target clients via the server

#### NB: Currently a work in progress...
