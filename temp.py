// Counter Worker for ai-assisted-novels.
// Proxies file requests from GitHub Pages and tallies them in KV.
//   GET /<book>/<file>.pdf|epub|png  -> count + return file
//   GET /stats                       -> JSON dump of counts
//
// PDFs are served inline; EPUB/PNG are served as downloads.
// Bot user-agents and Range requests are not counted.

const ORIGIN = "https://ralphbutler.github.io/ai-assisted-novels";

const BOT_UA_SUBSTRINGS = [
  "bot", "crawl", "spider", "slurp",
  "googlebot", "bingbot", "duckduckbot", "baiduspider", "yandexbot",
  "facebookexternalhit", "facebookcatalog",
  "slackbot", "twitterbot", "linkedinbot", "discordbot",
  "whatsapp", "telegrambot", "applebot",
  "redditbot", "pinterestbot", "embedly",
  "preview", "fetch", "monitoring", "uptime", "headless",
];

function isBot(request) {
  const ua = (request.headers.get("user-agent") || "").toLowerCase();
  if (!ua) return true;                       // blank UA -> treat as bot
  return BOT_UA_SUBSTRINGS.some(s => ua.includes(s));
}

function shouldCount(request) {
  if (request.headers.get("range")) return false;   // partial fetch -> skip
  if (isBot(request)) return false;
  return true;
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    // /stats -> JSON dump of all counts
    if (path === "/stats") {
      const list = await env.COUNTS.list();
      const data = {};
      for (const k of list.keys) {
        data[k.name] = await env.COUNTS.get(k.name);
      }
      return new Response(JSON.stringify(data, null, 2), {
        headers: { "Content-Type": "application/json" }
      });
    }

    // bare URL -> small landing message
    if (path === "/" || path === "") {
      return new Response(
        "Counter worker for ai-assisted-novels.\nVisit /stats for counts.",
        { headers: { "Content-Type": "text/plain" } }
      );
    }

    // only serve known file types; reject anything else
    const filename = path.split("/").pop();
    const ext = (filename.split(".").pop() || "").toLowerCase();
    const allowed = ["pdf", "epub", "png"];
    if (!allowed.includes(ext)) {
      return new Response("Not found.", { status: 404 });
    }

    // increment counter without blocking the response
    if (shouldCount(request)) {
      ctx.waitUntil((async () => {
        try {
          const n = parseInt(await env.COUNTS.get(path)) || 0;
          await env.COUNTS.put(path, String(n + 1));
        } catch (e) { /* swallow KV errors so the download still works */ }
      })());
    }

    // proxy from GitHub Pages
    const upstream = await fetch(ORIGIN + path);
    const headers = new Headers(upstream.headers);

    // PDFs open inline; EPUB and PNG force download
    if (ext !== "pdf") {
      headers.set("Content-Disposition", `attachment; filename="${filename}"`);
    }
    // defeat browser caching so repeat clicks register as repeat counts
    headers.set("Cache-Control", "no-store");

    return new Response(upstream.body, {
      status: upstream.status,
      statusText: upstream.statusText,
      headers,
    });
  }
};
