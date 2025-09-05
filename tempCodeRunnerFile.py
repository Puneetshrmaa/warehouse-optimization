import http.server
import socketserver

PORT = 8000

Handler = http.server.SimpleHTTPRequestHandler
Handler.extensions_map.update({
    '.json': 'application/json',
})

print("Starting server...")
print(f"Serving files on port {PORT}")
print("To view your dashboard, open this link in your browser:")
print(f"http://localhost:{PORT}/warehouseoptimizerresult.html")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()
