import http.server
import socketserver
import json
import urllib

from hw3 import search, suggest


class DemoHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/demo/suggest.json':
            qs = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
            if 'prefix' in qs and len(qs['prefix']) == 1:
                data = json.dumps(suggest(qs['prefix'][0])).encode('utf8')

                self.send_response(200)

                self.send_header('Content-type',
                                 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(data)
                return
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'bad request')
                return

        if parsed.path == '/demo/search.json':
            qs = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
            if 'query' in qs and len(qs['query']) == 1:
                result = [] if 'search' not in globals() else search(
                    qs['query'][0])
                data = json.dumps(result).encode('utf8')
                self.send_response(200)

                self.send_header('Content-type',
                                 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(data)
                return
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'bad request')
                return

        http.server.SimpleHTTPRequestHandler.do_GET(self)


if __name__ == '__main__':
    PORT = 8080
    with socketserver.TCPServer(("", PORT), DemoHandler) as httpd:
        print("Open demo at http://localhost:%d/demo/demo.html" % PORT)
        httpd.serve_forever()