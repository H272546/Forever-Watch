# Forever Watch

`index.html` is the source of the live artifact at https://claude.ai/artifact/8gFsdAENo1VF3WkjA9hx7G

## Adding a movie or TV show

1. Add an entry to `BUILT_INS` in `index.html`:
   `{id:'M64',title:'…',type:'movie'|'tv'|'doc',month:1-12,note:'…'}`
   - IDs are stable and never reused: next `M##` for films, `TV##` for series/docs, `WA##` for Woody Allen films.
   - Pick the month from `MONTHS` (season + mood, tuned to Ohio weather); write a one-line note in the same voice as the others.
   - Use `ONE UNIT ·` in the note for grouped titles.
2. Republish with the Artifact tool, passing `url` above (from a new session, read the artifact first).

Watch history lives in each viewer's browser `localStorage` and survives republishes; don't rename `STORAGE_KEY` or change existing IDs.

# Prep Kitchen (`cookbook/`)

`cookbook/index.html` is the source of the private artifact at https://claude.ai/artifact/X6LSnZiMah8t9o3bLz6VK5 (Fridge / Mood / Week modes over two purchased cookbooks).

- The recipe data (`recipes.json`, `img/*.webp`) is extracted from the owner's PDFs and is **not** in this public repo; it lives only in the artifact's published files. Never commit the PDFs or the extracted data.
- To rebuild the data: `python3 cookbook/build.py <meal-prep.pdf> <digital-cookbook.pdf> <out-dir>` (needs `pymupdf`, `pillow`). `cookbook/canon.py` maps ingredient lines to the ids used by Fridge matching and the shopping list.
- To change the app only, edit `cookbook/index.html` and republish with `url` above; published data files are kept when left out of `files`. Declared capability: `sample` with images (fridge photo scan).
- Viewer state is in `localStorage` under `prepkitchen.v1`; recipe ids (`a###` book 1 cover page, `b###` book 2 page) must stay stable.
