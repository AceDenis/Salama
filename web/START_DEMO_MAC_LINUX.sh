#!/bin/bash
cd "$(dirname "$0")"; echo "Open http://localhost:8080/index.html  (console: /console.html)"; python3 -m http.server 8080
