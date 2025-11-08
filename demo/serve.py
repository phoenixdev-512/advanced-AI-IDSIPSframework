#!/usr/bin/env python3
"""
Simple HTTP server to view the Project Argus demo webpage.
No dependencies required - uses Python's built-in http.server.
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# Set the port
PORT = 8080

# Change to demo directory
demo_dir = Path(__file__).parent
os.chdir(demo_dir)

# Custom handler to set proper MIME types
class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Set CORS headers for development
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

def main():
    """Start the demo server"""
    print("=" * 70)
    print("🛡️  Project Argus - Demo Server")
    print("=" * 70)
    print(f"\n📡 Starting demo server on port {PORT}...")
    print(f"📂 Serving files from: {demo_dir.absolute()}")
    print(f"\n🌐 Open your browser and navigate to:")
    print(f"\n    http://localhost:{PORT}/")
    print(f"    http://127.0.0.1:{PORT}/")
    print("\n💡 Press Ctrl+C to stop the server")
    print("=" * 70 + "\n")

    # Start server
    try:
        with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped. Thank you for viewing the Project Argus demo!")
        sys.exit(0)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ ERROR: Port {PORT} is already in use!")
            print(f"💡 Try a different port by editing this script, or stop the other service.")
            sys.exit(1)
        else:
            raise

if __name__ == "__main__":
    main()
