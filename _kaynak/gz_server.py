import http.server, gzip, os, sys
root = sys.argv[1]
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(s,*a,**k): super().__init__(*a, directory=root, **k)
    def send_head(s):
        path = s.translate_path(s.path)
        if os.path.isdir(path): path = os.path.join(path, 'index.html')
        if not os.path.exists(path): return super().send_head()
        data = open(path,'rb').read(); ctype = s.guess_type(path)
        gz = path.endswith(('.html','.txt','.xml')) and 'gzip' in s.headers.get('Accept-Encoding','')
        if gz: data = gzip.compress(data)
        s.send_response(200); s.send_header('Content-Type', ctype)
        if gz: s.send_header('Content-Encoding','gzip')
        s.send_header('Content-Length', str(len(data))); s.send_header('Cache-Control','max-age=3600'); s.end_headers()
        import io; return io.BytesIO(data)
    def log_message(s,*a): pass
http.server.ThreadingHTTPServer(('127.0.0.1',8766),H).serve_forever()
