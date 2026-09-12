# prasannamalode.in

Personal site of Prasanna Malode — essays on DevSecOps, cybersecurity, AI governance and IT leadership, plus a set of free browser-based tools.

Static HTML, hosted on GitHub Pages. No framework, no runtime dependencies, no build server. A small Python script turns markdown into article pages.

## Layout

```
index.html              Home / Articles / Tools / About (hash-routed single page)
404.html                Not-found page
content/*.md            Article sources (front matter + markdown)  <- edit these
articles/*.html         Generated article pages + 3 stand-alone guides
tools/*.html            Interactive tools (self-contained)
assets/site.css         Design system (light + dark)
assets/site.js          Shared behaviour (router, search, theme, TOC, share)
assets/articles-data.js Generated article index used by the pages
assets/og/*.png         Generated social preview images
feed.xml, sitemap.xml   Generated
build.py                The generator
```

## Adding an article

1. Create `content/my-article.md`:

   ```
   ---
   id: my-article
   title: The title
   tag: DevSecOps
   date: 2026-10-01
   summary: One sentence that appears in cards, RSS and social previews.
   series: Optional series name
   part: 3
   ---

   Body in markdown. Headings (##), paragraphs, **bold**, *italics*, lists,
   > blockquotes, `code`, fenced code blocks and [links](https://…) are supported.
   ```

   `read` is computed from word count unless you set it.

2. Run `python3 build.py`.
3. Commit `content/`, `articles/`, `assets/articles-data.js`, `articles.json`, `feed.xml`, `sitemap.xml`, `assets/og/`.

Pillow (`pip install pillow`) is optional and only used to render the social preview images.

## Local preview

```
python3 -m http.server 8080
```

Then open http://localhost:8080/.
