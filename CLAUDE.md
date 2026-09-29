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
