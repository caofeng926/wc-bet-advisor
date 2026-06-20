const http = require("http");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..", "preview", "dist");
const PORT = 5173;
const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".ico": "image/x-icon",
  ".json": "application/json; charset=utf-8",
};

http.createServer((req, res) => {
  const url = decodeURIComponent((req.url || "/").split("?")[0]);
  let p = path.join(ROOT, url);
  if (!p.startsWith(ROOT)) { res.writeHead(403); res.end("forbidden"); return; }
  fs.stat(p, (err, st) => {
    const serve = (fp) => {
      res.writeHead(200, { "Content-Type": MIME[path.extname(fp)] || "application/octet-stream" });
      fs.createReadStream(fp).pipe(res);
    };
    if (!err && st.isFile()) return serve(p);
    if (url.startsWith("/assets/") || path.extname(url)) { res.writeHead(404); res.end("not found"); return; }
    serve(path.join(ROOT, "index.html"));
  });
}).listen(PORT, "127.0.0.1", () => console.log(`serving ${ROOT} on http://127.0.0.1:${PORT}`));
