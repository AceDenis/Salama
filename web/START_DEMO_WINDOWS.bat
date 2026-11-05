@echo off
echo Starting the Salama demo. Open http://localhost:8080/index.html in your browser.
echo Staff console: http://localhost:8080/console.html   (same browser)
echo Close this window to stop.
start http://localhost:8080/index.html
py -m http.server 8080 || python -m http.server 8080
