# ai-assisted-novels


## 📊 Download counter (Cloudflare Worker)

Download links on each book page don't point at GitHub Pages directly. They go
through a Cloudflare Worker that tallies the hit in a KV namespace and then
proxies the file from Pages:

    https://ai-assisted-novel-downloads.rmbgm1.workers.dev/<book>/<file>

- Source: `assets/counter-worker.js` — this repo holds the copy of record, but
  the live code is deployed by pasting it into the Cloudflare dashboard
  (Workers & Pages → `ai-assisted-novel-downloads` → Edit code → Deploy).
  Editing the file here changes nothing until it is deployed.
- Counts: <https://ai-assisted-novel-downloads.rmbgm1.workers.dev/stats> (JSON).
  KV keys are the URL path, created on first real download.
- Only `.pdf`, `.epub`, and `.png` are proxied. JPG covers are served straight
  from Pages and are never counted.
- Not counted: bot user-agents, blank user-agents, `Range` requests, and any
  request where the upstream fetch doesn't return 200.

**Nothing here needs changing when a book is added.** The Worker has no list of
books. Adding the slug to `BOOKS` in `assets/build_book_pages.py` and running it
writes the Worker download links into the new book page, and the counter starts
on the first download.
