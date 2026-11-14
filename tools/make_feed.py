"""Build feed.xml (RSS 2.0) for Amwaj Magazine from archive/issues.json.

One feed item per weekly issue. Also adds the feed <link> to index.html
and every issues/*/index.html if it is missing. Run from the repo root.
"""
import glob, json, html, datetime, os

SITE = "https://magazine.amwaj.media"
TITLE = "Amwaj Magazine"
DESC = ("The week's reporting and analysis from Amwaj.media on Iran, Iraq "
        "and the Arabian Peninsula.")
LINK_TAG = ('<link rel="alternate" type="application/rss+xml" '
            'title="Amwaj Magazine" href="/feed.xml">')

def rfc822(day):
    d = datetime.datetime.strptime(day, "%Y-%m-%d").replace(
        hour=6, tzinfo=datetime.timezone.utc)
    return d.strftime("%a, %d %b %Y %H:%M:%S +0000")

issues = json.load(open("archive/issues.json", encoding="utf-8"))
issues.sort(key=lambda i: i["number"], reverse=True)

items = []
for i in issues:
    url = SITE + i.get("url", "/")
    thumb = SITE + "/archive/" + i["thumb"] if i.get("thumb") else ""
    t = i["title"].rstrip()
    t = t if t[-1:] in "?!." else t + "."
    summary = f'Issue {i["number"]} ({i["range"]}): {t}'
    if i.get("stories"):
        summary += f' {i["stories"]} stories.'
    body = (f'<p><img src="{thumb}" alt=""></p>' if thumb else "") + \
           f"<p>{html.escape(summary)}</p>"
    items.append(f"""  <item>
    <title>{html.escape(f'Issue {i["number"]}: {i["title"]}')}</title>
    <link>{url}</link>
    <guid isPermaLink="false">amwaj-magazine-issue-{i["number"]}</guid>
    <pubDate>{rfc822(i["added"])}</pubDate>
    <description>{html.escape(summary)}</description>
    <content:encoded><![CDATA[{body}]]></content:encoded>
""" + (f'    <media:content url="{thumb}" medium="image"/>\n' if thumb else "")
      + "  </item>")

latest = rfc822(issues[0]["added"]) if issues else ""
feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:media="http://search.yahoo.com/mrss/">
<channel>
  <title>{TITLE}</title>
  <link>{SITE}/</link>
  <atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>
  <description>{html.escape(DESC)}</description>
  <language>en</language>
  <lastBuildDate>{latest}</lastBuildDate>
  <image><url>{SITE}/logo.png</url><title>{TITLE}</title><link>{SITE}/</link></image>
{chr(10).join(items)}
</channel>
</rss>
"""
open("feed.xml", "w", encoding="utf-8").write(feed)

for page in ["index.html", "archive/index.html"] + glob.glob("issues/*/index.html"):
    if not os.path.exists(page):
        continue
    text = open(page, encoding="utf-8").read()
    if "application/rss+xml" not in text and "</head>" in text:
        open(page, "w", encoding="utf-8").write(
            text.replace("</head>", LINK_TAG + "\n</head>", 1))
print(f"feed.xml written with {len(items)} issues")
