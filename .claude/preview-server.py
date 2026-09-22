"""Minimal static file server for local preview (python3 .claude/serve.py [port]).

Sends no-store headers so edits show up on reload without cache fighting.
This is a development convenience only — it is not used in production.
"""
import functools, http.server, socketserver, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4173


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("%s\n" % (fmt % args))


Handler = functools.partial(Handler, directory=ROOT)


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


with Server(("127.0.0.1", PORT), Handler) as httpd:
    print("serving %s on http://localhost:%d" % (ROOT, PORT), flush=True)
    httpd.serve_forever()
