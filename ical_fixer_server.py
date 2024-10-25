import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from ical_fixer import IcalFixer

class IcalFixerServer(BaseHTTPRequestHandler):
    def do_GET(self):
        with open("config.json") as config_file:
            config = json.load(config_file)

        if self.path == config["ICS_URL_PATH"]:
            ical_fixer = IcalFixer(config["ICS_REMOTE_URL"])
            data = ical_fixer.convert()

            if data:
                self.send_response(200)
                self.send_header("ContentType", "txt/calendar")
                self.end_headers()

                self.wfile.write(data.encode('utf-8'))
            else:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"Error while converting file.")
        else:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Forbidden")


if __name__ == "__main__":
    # Define server settings
    PORT = 8080
    server_address = ("", PORT)

    # Run the server
    httpd = HTTPServer(server_address, IcalFixerServer)
    print(f"Serving on port {PORT}")
    httpd.serve_forever()
