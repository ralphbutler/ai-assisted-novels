#!/usr/bin/env python3
"""Generate per-book HTML pages from a single template.
Each book's metadata: title, teaser (short visible blurb), meta_desc (longer
description for crawlers + link previews), author's note (optional), and genre list.
"""
import json
import pathlib

ROOT = pathlib.Path("/Users/rbutler/GitHub/ai-assisted-novels")
SITE = "https://ralphbutler.github.io/ai-assisted-novels"
# Cloudflare Worker that proxies PDF/EPUB downloads and counts each one in KV.
# PDFs are returned inline; EPUBs as attachments. The PNG cover link bypasses this
# and points straight at GitHub Pages so cover-thumbnail clicks aren't counted.
WORKER = "https://ai-assisted-novel-downloads.rmbgm1.workers.dev"

# Em-dash flanked by hair-spaces (matches the homepage typography).
M = "&thinsp;&mdash;&thinsp;"
# Smart quotes / ellipsis shortcuts.
LQ, RQ = "&lsquo;", "&rsquo;"

BOOKS = {
    "lifecycle_completion": {
        "title_html":  "Lifecycle Completion",
        "title_plain": "Lifecycle Completion",
        "note":        "Our most relatable novel, by far.",
        "teaser":      (
            "Claire Nakamura works in HR at a health insurance company where every executive "
            f"on the org chart is a psychopath{M}and she has the diagnostic tools on her desk to prove it. "
            "When a member dies because a doctor spent ninety seconds on his file, she stops observing "
            "and starts engineering. Three executives. One circular firing squad."
        ),
        "meta_desc": "An HR analyst engineers a circular firing squad of psychopath executives at a health insurance company. A dark comedy of corporate revenge by Ralph M. Butler.",
        "genres": ["Dark Comedy", "Corporate Satire"],
    },
    "case_borrowed_alibi": {
        "title_html":  "The Case of the Borrowed Alibi",
        "title_plain": "The Case of the Borrowed Alibi",
        "note":        (
            "A classic Perry Mason formula{m}bought alibis, courtroom traps, Della and Paul "
            "running the case with Perry. The characters are drawn from the Raymond Burr television "
            f"series of the late 1950s and 1960s rather than the Gardner paperbacks. A modern twist: "
            f"the reader follows the investigation with the {LQ}Columbo{RQ} license of seeing the "
            f"pieces fall into place{M}the thrill isn{RQ}t just the {LQ}Who,{RQ} but the {LQ}How.{RQ}"
        ).format(m=M),
        "teaser": (
            f"Summer 1971. A Hollywood stuntman walks into Perry Mason{RQ}s office with a confession that "
            f"could end his career{M}and send him to prison. He{RQ}s been selling alibis for a powerful "
            f"studio producer{RQ}s Tuesday nights, and now that producer{RQ}s wife has been found "
            "strangled in their Hollywood Hills home."
        ),
        "meta_desc": "A Perry Mason mystery in summer 1971: a stuntman who sells alibis becomes the only thing standing between a Hollywood producer and a murder conviction.",
        "genres": ["Mystery", "Legal Thriller"],
    },
    "observation_car": {
        "title_html":  "The Observation Car",
        "title_plain": "The Observation Car",
        "note": (
            f"Not a locked-room puzzle built for Poirot{M}a cozy mystery in the tradition of "
            f"Richard Osman{RQ}s Thursday Murder Club: warm, domestic, and deceptively sharp. "
            f"Similar to Osman{RQ}s {LQ}Joyce{RQ} chapters, the odd-numbered chapters here are narrated "
            "by Hazel, a retired midwife and school secretary in her early seventies who notices everything. "
            f"Her voice runs on tea, biscuits, and quiet observation. The even-numbered chapters show what "
            f"she can{RQ}t see."
        ),
        "teaser": (
            f"Three retired Americans{M}a school-secretary/midwife, a U.S. Marshal, and an actuary{M}"
            "are on a luxury train through the Rockies when the billionaire who chartered it dies in his "
            "locked suite before the Welcome Dinner. The official verdict is altitude sickness. They know "
            "better. Then a snowstorm strands them in the mountains."
        ),
        "meta_desc": "A cozy mystery on a luxury train through the Rockies. A billionaire dies in his locked suite, and three retired Americans know the official verdict is wrong.",
        "genres": ["Cozy Mystery"],
    },
    "standing_ground": {
        "title_html":  "Standing Ground",
        "title_plain": "Standing Ground",
        "note": None,
        "teaser": (
            f"A Washington analyst blows the whistle on a mining conglomerate seizing land from "
            f"communities{M}and discovers his own agency helped bury the evidence. His career doesn{RQ}t "
            f"survive. He flies to Central Australia to disappear at his cousin{RQ}s cattle station, only "
            "to find the same company pressuring fourteen pastoral families off their leases."
        ),
        "meta_desc": "A disgraced government analyst flees to a Central Australian cattle station, only to find the same mining conglomerate that ruined him operating there.",
        "genres": ["Thriller", "Contemporary Fiction"],
    },
    "makenas_walk": {
        "title_html":  f"Makena{RQ}s Walk",
        "title_plain": "Makena’s Walk",
        "note": (
            f"A friend gave me a copy of {LQ}Elephant Company{RQ} about Billy Williams, who worked in "
            "colonial Burma as a forest man for a British teak company in 1920. He was amazed by the "
            f"intelligence and character of elephants who hauled logs through the jungle. He became the "
            f"{LQ}elephant wallah.{RQ} It was fascinating to learn about their traits, and I have tried to "
            "incorporate some of that into this book."
        ),
        "teaser": (
            f"1965 Kenya. A ceremonial elephant named Makena has walked away from her handlers{M}"
            "not stolen, not lost, but retired. She picked a direction and left with the certainty "
            "of someone who had been planning it. A small expedition is hired to find her and bring "
            "her back. They find her. She is calm, healthy, and content. She does not want to return."
        ),
        "meta_desc": "1965 Kenya: a ceremonial elephant has walked away from her handlers, not lost but retired. A small expedition finds her, and she does not want to come back.",
        "genres": ["Adventure", "Historical Fiction"],
    },
    "against_the_sun": {
        "title_html":  "Against the Sun",
        "title_plain": "Against the Sun",
        "note": (
            f"I have a tiny thread of Cherokee ancestry{M}too little to claim anything by, "
            "but enough to pull me toward this story."
        ),
        "teaser": (
            "A Cherokee survivor of the Trail of Tears walks out of the wilderness and into a Comanche "
            "camp on the Texas plains. He carries a proposal: travel east to Washington and the Hermitage "
            f"to kill the men responsible for the forced removal of his people. Four Comanche{M}who have "
            f"their own debts to settle with the army{M}agree to go with him. It is 1838."
        ),
        "meta_desc": "1838: a Cherokee survivor of the Trail of Tears and four Comanche ride east to find the men behind Indian Removal — Jackson, Van Buren, Poinsett.",
        "genres": ["Historical Fiction"],
    },
    "dead_letter_men": {
        "title_html":  "The Dead Letter Men",
        "title_plain": "The Dead Letter Men",
        "note": None,
        "teaser": (
            "A rider vanishes on the Pony Express trail in central Nevada. His horse is gone, his mail "
            "pouch is tucked under sage at the road's edge, and there is no blood. The company sends two "
            f"men to find out what happened{M}a tracker who reads dirt and a lawyer who reads people. "
            "It is spring 1861. Fort Sumter has fallen. The country is cracking apart."
        ),
        "meta_desc": "Spring 1861, Pony Express country: a rider vanishes, his mail pouch tucked under sage. Two investigators uncover a forgery operation tied to the coming Civil War.",
        "genres": ["Historical Mystery", "Western"],
    },
    "scopes20": {
        "title_html":  "Scopes 2.0",
        "title_plain": "Scopes 2.0",
        "note": (
            "This novella was not written as a serious literary undertaking. It was a small experiment "
            f"in AI-assisted fiction{M}a test bed for trying different prompting techniques, voice "
            "calibrations, and collaborative workflows between human and machine. The writing styles "
            "may shift as a result. Think of it as a lab notebook that happens to tell a story."
        ),
        "teaser": (
            "In 2024, Tennessee passes a law banning the teaching of evolution in public schools. "
            "Sarah Chen, a high school biology teacher in the small town of Oakville, teaches it anyway "
            "and is arrested in her classroom. What follows is a courtroom drama that mirrors the 1925 "
            f"Scopes Monkey Trial{M}same state, same statute, played out a century later under "
            f"fluorescent lights, with a Fitbit tracking the defendant{RQ}s heart rate."
        ),
        "meta_desc": "In 2024 Tennessee bans teaching evolution. A biology teacher refuses, and her trial becomes a modern echo of the 1925 Scopes Monkey Trial.",
        "genres": ["Legal Drama"],
    },
    "juror_nine": {
        "title_html":  "Juror Nine",
        "title_plain": "Juror Nine",
        "note":        "This short novel is an attempt to match the style of Elmore Leonard in a fun story about a hitman that ends up on the jury for his target.",
        "teaser": (
            "Dan Mercer teaches history at a Nashville university and quietly works as a hitman on the side. "
            f"When a local contract lands on his desk, the target gets arrested for murder before Dan can act{M}"
            f"and then Dan is summoned for jury duty on the same trial. He{RQ}s seated as Juror Nine. "
            f"His target is at the defendant{RQ}s table."
        ),
        "meta_desc": "A Nashville history professor moonlighting as a hitman ends up on the jury for the man he was hired to kill. An AI-assisted novel by Ralph M. Butler, modeled on Elmore Leonard.",
        "genres": ["Crime Fiction"],
    },
    "uncatalogued_book": {
        "title_html":  "The Uncatalogued Book",
        "title_plain": "The Uncatalogued Book",
        "note": (
            "Perhaps our most difficult-to-read book thus far. Every paragraph tries to meet two "
            "goals at once:"
            "<ol>"
            "<li>sound as if spoken by a tradesman in rare manuscripts living in 1620;</li>"
            "<li>keep its meaning easily discernible to someone living in 2020.</li>"
            "</ol>"
        ),
        "teaser": (
            f"Niccolò, a book trader in his eighties, is passing what he knows to his young apprentice. "
            f"Long ago he learned the trade{RQ}s hard secret: the most valuable books are the banned "
            f"ones, because power fears the truth, and the truth is most often written by those it has "
            f"labeled heretics. For sixty years he is sent wherever books break loose{M}failing "
            f"monasteries, plague estates, collapsing courts{M}until, in 1659 Mughal Delhi, he makes "
            "the purchase of his life out of the wreckage of an execution, and can never enter it in "
            "any catalogue."
        ),
        "meta_desc": "An eighty-year-old manuscript trader recounts sixty years buying banned books across the seventeenth century — Venice, Constantinople, Isfahan, Mughal Delhi — and the one purchase he could never enter in any catalogue. A literary historical novel by Ralph M. Butler.",
        "genres": ["Historical Fiction"],
        "extra_files": [("COMPANION_GUIDE.pdf", "PDF Document")],
    },
}


# scopes20 has no image file listed as a separate download (per current layout); others do.
# (Actually all 9 books include the .png in the download list per the structure we standardized.)
EXTRAS_FOR = {  # any per-book overrides go here if needed
}


TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title_html} &mdash; A Novel by Ralph M. Butler</title>
    <meta name="description" content="{meta_desc}">
    <link rel="canonical" href="{canonical}">

    <!-- Browser tab + home-screen icons (located at site root, one directory up) -->
    <link rel="icon" type="image/png" href="../favicon.png">
    <link rel="apple-touch-icon" href="../apple-touch-icon.png">

    <!-- Open Graph -->
    <meta property="og:type" content="book">
    <meta property="og:site_name" content="AI-Assisted Novels">
    <meta property="og:title" content="{title_plain}">
    <meta property="og:description" content="{meta_desc}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:image" content="{image_url}">
    <meta property="og:image:alt" content="{title_plain} book cover">
    <meta property="book:author" content="Ralph M. Butler">

    <!-- Twitter card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title_plain}">
    <meta name="twitter:description" content="{meta_desc}">
    <meta name="twitter:image" content="{image_url}">

    <meta name="theme-color" content="#2a2218">

    <!-- Schema.org Book markup. Tells Google "this page is a book"; can produce a richer search result. -->
    <script type="application/ld+json">
{json_ld}
    </script>

    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            max-width: 820px;
            margin: 40px auto;
            padding: 0 20px;
            color: #333;
        }}
        .back-link {{
            display: inline-block;
            margin-bottom: 24px;
            color: #0066cc;
            text-decoration: none;
            font-size: 0.95em;
        }}
        .back-link:hover {{ text-decoration: underline; }}

        .book-header {{
            display: flex;
            gap: 28px;
            margin-bottom: 32px;
        }}
        .book-cover {{
            flex-shrink: 0;
        }}
        .book-cover img {{
            width: 220px;
            height: auto;
            border-radius: 4px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.2);
            display: block;
        }}
        .book-meta h1 {{
            margin: 0 0 4px;
            font-size: 1.9rem;
        }}
        .book-meta .byline {{
            color: #666;
            font-style: italic;
            margin: 0 0 18px;
        }}
        .author-note {{
            background: #f5f0e6;
            border-left: 3px solid #b8882e;
            padding: 12px 16px;
            font-size: 0.95em;
            color: #4a3d20;
            margin: 0 0 18px;
            font-style: italic;
        }}
        .author-note ol {{
            margin: 8px 0 0;
            padding-left: 22px;
        }}
        .author-note li {{
            margin: 4px 0;
            padding: 0;
            background: none;
            display: list-item;
        }}
        .description {{
            margin: 0;
            line-height: 1.65;
        }}

        h2 {{
            border-bottom: 2px solid #eee;
            padding-bottom: 8px;
            margin-top: 40px;
            font-size: 1.2rem;
        }}
        ul {{
            list-style: none;
            padding: 0;
        }}
        li {{
            margin: 15px 0;
            padding: 10px;
            background: #f9f9f9;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        a {{
            color: #0066cc;
            text-decoration: none;
            font-weight: bold;
        }}
        a:hover {{ text-decoration: underline; }}
        .notice {{
            background: #fff8e1;
            border-left: 4px solid #d4a84b;
            padding: 14px 18px;
            font-size: 1.1em;
            color: #5a4a1a;
            margin: 20px 0 28px;
            border-radius: 4px;
        }}
        .file-info {{
            font-size: 0.9em;
            color: #666;
        }}

        @media (max-width: 640px) {{
            .book-header {{
                flex-direction: column;
                align-items: center;
                text-align: center;
            }}
            .book-cover img {{ width: 180px; }}
        }}
    </style>
</head>
<body>
    <a href="../" class="back-link">&larr; All novels</a>

    <div class="book-header">
        <div class="book-cover">
            <img src="{slug}.png" alt="{title_plain} book cover">
        </div>
        <div class="book-meta">
            <h1>{title_html}</h1>
            <p class="byline">A novel by Ralph M. Butler and Claude Opus</p>
{note_block}            <p class="description">
                {teaser}
            </p>
        </div>
    </div>

    <h2>Available Files</h2>
    <p class="notice">
        <strong>PDFs</strong> open in your browser when clicked. <strong>EPUB</strong> and <strong>image</strong> files download automatically. Right-click any link and choose &ldquo;Save Link As&hellip;&rdquo; to save.
    </p>
    <ul>
        <li>
            <a href="{worker}/{slug}/{slug}.pdf">{slug}.pdf</a>
            <span class="file-info">PDF Document</span>
        </li>
        <li>
            <a href="{worker}/{slug}/{slug}.epub" download="{slug}.epub">{slug}.epub</a>
            <span class="file-info">eBook (EPUB)</span>
        </li>
        <li>
            <a href="{slug}.png" download="{slug}.png">{slug}.png</a>
            <span class="file-info">Image</span>
        </li>
{extra_files}    </ul>
</body>
</html>
"""


def render(slug, b):
    canonical = f"{SITE}/{slug}/{slug}.html"
    image_url = f"{SITE}/{slug}/{slug}.png"

    json_ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Book",
        "name": b["title_plain"],
        "author": {"@type": "Person", "name": "Ralph M. Butler"},
        "image": image_url,
        "url": canonical,
        "description": b["meta_desc"],
        "inLanguage": "en",
        "genre": b["genres"] if len(b["genres"]) > 1 else b["genres"][0],
    }, indent=8)
    # Indent the whole JSON block for visual nesting under <script>.
    json_ld = "        " + json_ld.replace("\n", "\n        ")

    note_block = ""
    if b["note"]:
        note_block = f'            <div class="author-note">\n                {b["note"]}\n            </div>\n'

    # Optional extra downloads living directly in the book's own dir (not the
    # Worker-proxied pdf/epub). Each entry is (filename, file-info label).
    extra_files = ""
    for fname, info in b.get("extra_files", []):
        extra_files += (
            f'        <li>\n'
            f'            <a href="{fname}" download="{fname}">{fname}</a>\n'
            f'            <span class="file-info">{info}</span>\n'
            f'        </li>\n'
        )

    return TEMPLATE.format(
        slug=slug,
        title_html=b["title_html"],
        title_plain=b["title_plain"],
        meta_desc=b["meta_desc"],
        canonical=canonical,
        image_url=image_url,
        json_ld=json_ld,
        teaser=b["teaser"],
        note_block=note_block,
        extra_files=extra_files,
        worker=WORKER,
    )


for slug, b in BOOKS.items():
    path = ROOT / slug / f"{slug}.html"
    path.write_text(render(slug, b))
    print(f"wrote: {path.relative_to(ROOT)}")
