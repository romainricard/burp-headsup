import socket
import SocketServer
import time
from BaseHTTPServer import BaseHTTPRequestHandler
from burp import IBurpExtender
from burp import IExtensionStateListener
from functools import partial
from urlparse import urlparse, parse_qs

HOSTNAME = ""
PORT_NUMBER = 8042
KEY = "3ce7a61896d5fe8729_DEFAULT_KEY_CHANGEME_287ad2ac2d7b9"  # CHANGEME

# Duration for Burp to switch proxy on/off, see README.md
TOGGLE_EXECUTION_DURATION = 0.01


class CustomTCPServer(SocketServer.TCPServer):
    """
    Allows to free the port after shutdown
    """

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)


class CustomHTTPHandler(BaseHTTPRequestHandler, object):
    def __init__(self, callbacks, *args, **kwargs):
        self.callbacks = callbacks
        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def send_fullresponse(self, http_code, content):
        self.send_response(http_code)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(content.encode("utf8"))

    def do_GET(self):

        state = ""

        request_parsed = urlparse(self.path)
        request_path = request_parsed.path

        try:
            request_key = parse_qs(request_parsed.query).get("key", "")[0]
        except IndexError:
            request_key = None

        if request_key != KEY:
            self.send_fullresponse(403, "Wrong key")
            return

        if request_path == "/burp-status":
            state = "RUNNING"
        elif request_path == "/proxy/enable":
            self.callbacks.setProxyInterceptionEnabled(True)
            state = "INTERCEPT"
        elif request_path == "/proxy/disable":
            self.callbacks.setProxyInterceptionEnabled(False)
            state = "PASS"
        elif request_path == "/proxy/toggle":
            # Here's the real twist: even if setProxyInterceptionEnabled()
            # exists, its getter version does not exists. So how to know the
            # current state of the proxy to toggle it? By timing it! See
            # README.md

            # I've chose setProxyInterceptionEnabled(True) in order to not free
            # a catched request. Feel free to reverse the logic if you need.
            start_time = time.time()
            self.callbacks.setProxyInterceptionEnabled(True)
            stop_time = time.time()

            if stop_time - start_time > TOGGLE_EXECUTION_DURATION:
                # proxy was off, no problem, we've just toggled it
                state = "INTERCEPT"
            else:
                # proxy was already on, so we need to toggle it
                self.callbacks.setProxyInterceptionEnabled(False)
                state = "PASS"
        else:
            # Unhandled path
            self.send_fullresponse(404, "Unknown path.")
            return

        self.send_fullresponse(200, state)


class BurpExtender(IBurpExtender, IExtensionStateListener):
    def registerExtenderCallbacks(self, callbacks):
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName("Burp head-up")

        # Used for extensionUnloaded
        callbacks.registerExtensionStateListener(self)

        handler = partial(CustomHTTPHandler, callbacks)
        self.httpd = CustomTCPServer((HOSTNAME, PORT_NUMBER), handler)
        self.httpd.serve_forever()

    def extensionUnloaded(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        print("Server stopped.")

