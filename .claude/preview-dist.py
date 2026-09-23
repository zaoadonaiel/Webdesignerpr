"""Local preview: build the site, then serve dist/ (dev convenience only)."""
import functools, http.server, os, runpy, socketserver, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

runpy.run_path(os.path.join(ROOT, "build.py"), run_name="__build__")

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4173


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


handler = functools.partial(Handler, directory=os.path.join(ROOT, "dist"))
with Server(("127.0.0.1", PORT), handler) as httpd:
    print("serving dist/ on http://localhost:%d" % PORT, flush=True)
    httpd.serve_forever()
