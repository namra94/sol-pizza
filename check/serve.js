// A local stand-in for the sol-pizza Worker's static assets, for the checks:
// dist/_redirects (exact and splat rules, query kept), directory index pages,
// /x served from x.html, and the nearest 404.html with a 404 status.
// Not the real thing (no _headers, no compression, no Worker): Lighthouse budgets
// are for the Preview URL; this is for axe, behaviour and screenshots.
const http = require('http'), fs = require('fs'), path = require('path');
const TYPES = {'.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript',
               '.svg': 'image/svg+xml', '.woff2': 'font/woff2', '.png': 'image/png', '.xml': 'application/xml',
               '.txt': 'text/plain'};

function rules(dist) {
  const f = path.join(dist, '_redirects');
  if (!fs.existsSync(f)) return [];
  return fs.readFileSync(f, 'utf8').split('\n').map(l => l.trim().split(/\s+/))
    .filter(p => p.length >= 2 && !p[0].startsWith('#')).map(([from, to, code]) => ({from, to, code: +(code || 302)}));
}

module.exports = function serve(dist, port) {
  const redirects = rules(dist);
  return new Promise(resolve => {
    const server = http.createServer((req, res) => {
      const url = new URL(req.url, 'http://localhost');
      const p = decodeURIComponent(url.pathname);
      for (const r of redirects) {
        const splat = r.from.endsWith('*') && p.startsWith(r.from.slice(0, -1));
        if (p === r.from || splat) {
          const to = r.to.replace(':splat', splat ? p.slice(r.from.length - 1) : '');
          res.writeHead(r.code, {Location: to + (to.includes('?') || to.includes('#') ? '' : url.search)});
          return res.end();
        }
      }
      let f = path.join(dist, p);
      if (p.endsWith('/')) f = path.join(f, 'index.html');
      else if (!fs.existsSync(f) && fs.existsSync(path.join(f, 'index.html'))) {
        res.writeHead(307, {Location: p + '/' + url.search});
        return res.end();
      }
      if (!fs.existsSync(f) && fs.existsSync(f + '.html')) f += '.html';
      let status = 200;
      if (!fs.existsSync(f) || fs.statSync(f).isDirectory()) {
        status = 404;
        f = null;
        for (let d = path.dirname(path.join(dist, p)); d.startsWith(dist); d = path.dirname(d)) {
          if (fs.existsSync(path.join(d, '404.html'))) { f = path.join(d, '404.html'); break; }
        }
        if (!f) { res.writeHead(404); return res.end('not found'); }
      }
      res.writeHead(status, {'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream'});
      fs.createReadStream(f).pipe(res);
    });
    server.listen(port, () => resolve(server));
  });
};
