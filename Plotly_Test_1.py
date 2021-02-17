# !/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import random
import json
import time

def send_header(BaseHTTPRequestHandler):
    BaseHTTPRequestHandler.send_response(200)
    BaseHTTPRequestHandler.send_header('Access-Control-Allow-Origin', '*')
    BaseHTTPRequestHandler.send_header('Content-type:', 'application/json')
    BaseHTTPRequestHandler.end_headers()


class MyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # returns the temperature
        if self.path == '/temperature':
            send_header(self)
            self.wfile.write(bytes(json.dumps({'time': time.strftime('%H:%M:%S', time.gmtime()), 'temperature': random.randint(0, 100)}), 'utf-8'))

if __name__ == '__main__':
    # start server
    server = HTTPServer(('', 8099), MyRequestHandler)
    server.serve_forever()

    def do_GET(self):
        html = '''
            <html>
            <head>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <script>
            var temperatures;
            var temperatures_x = [];
            var temperatures_y = [];
            var server_url = "";

            //basic request handler
            function createRequest() {
                var result = null;
                if (window.XMLHttpRequest) {
                    // FireFox, Safari, etc.
                    result = new XMLHttpRequest();
                    if (typeof result.overrideMimeType != "undefined") {
                        result.overrideMimeType("text/xml"); // Or anything else
                    }
                } else if (window.ActiveXObject) {
                    // MSIE
                    result = new ActiveXObject("Microsoft.XMLHTTP");
                }
                return result;
            }
            //gets the temperature from the Python3 server
            function update_temperatures() {
                var req = createRequest();
                req.onreadystatechange = function () {
                    if (req.readyState !== 4) {
                        return;
                    }
                    temperatures = JSON.parse(req.responseText);
                    return;
                };
                req.open("GET", server_url + "/temperature", true);
                req.send();
                return;
            }

            //updates the graph
            function update_graph() {
                update_temperatures();
                temperatures_x.push(temperatures.time)
                temperatures_y.push(temperatures.temperature)
                Plotly.newPlot('graph_t', [{x: temperatures_x, y: temperatures_y}]);
            }

            //initializes everything
            window.onload = function () {
                document.getElementById("url").onchange = function () {
                    server_url = document.getElementById("url").value;
                };
                server_url = document.getElementById("url").value;
                //timer for updating the functions
                var t_cpu = setInterval(update_graph, 1000);
            };

             </script>
            </head>

            <body>
                <li>
                    URL and port<input type="text" id="url" value="http://localhost:8099">
                </li>
                <div class="plotly_graph" id="graph_t"></div>
            </body>
            </html>

        '''