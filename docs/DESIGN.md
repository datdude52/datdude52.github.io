# Design decisions

Read this before changing anything visual or editorial.

- **Round 1** came from a four-advisor council: hiring manager, type designer, performance/accessibility engineer, and devil's advocate. The brief is in [council-brief.md](council-brief.md).
- **Round 2** (Oct 2026) added Andrew's direction: more color, links as blocks, real pages behind every link, the resume shown on the page, and copy written in his own voice.
- **Round 3** (Oct 19, 2026) came from research on what recruiters and hiring engineers screen for. It added the screening facts in the hero, skills linked to evidence, optional "What I learned" sections, and phone touch fixes. The open content list is [CONTENT_GAPS.md](CONTENT_GAPS.md).
- **Round 4** (Oct 20, 2026) ran the design-taste-frontend skill (direction "The contact sheet", seed 1141376720, palette and type kept) and find-animation-opportunities plus animate for motion. It replaced the home hero with the name at display size over a contact sheet of every project's pictures, added the ARC-001 scan as the site's one interactive piece, removed every 1px outline and divider in favor of tone steps, cut the type to five sizes, set running text in full ink, and added three motions. Inspector results are in `.taste-skill/` (git-ignored).

## Principle

> The tell is assembling generic parts without content, not any single part.

Distinctiveness comes from real engineering evidence: photos of hardware, plots made from real data, annotated figures, and numbers. Styling isn't where it comes from.

## Current decisions

| Area | Decision |
|---|---|
| Pages | Home, Projects, a page per project, Resume, About, and 404. Every nav link is a real page. |
| Palette | Navy `#12284A` for the header, home hero, and footer bands. Drawing blue `#1F4E9C` for links, primary blocks, and figure annotations. Sky `#E8EEF8` for the spec panel and block hover. Canvas `#F3F5F8` page background with white panels. Ink `#1A1A1A`, muted `#55606E`. Burnt orange `#C2410C` appears only in plots, as the ultrasonic series. |
| Type | IBM Plex Sans, self-hosted, for the site. Carlito (metric-compatible with Calibri) for the resume sheet, matching the Word template. |
| Links | Calls to action are filled rectangular blocks with a 6px radius and no outline: primary (blue), default (sky), white on navy, and navy-2 on navy. Nav links are filled blocks too, and the current page is white. Inline prose links stay underlined. |
| Projects | On the Projects page: two-ended list rows (4:3 thumbnail, title and result, dates at the right end), not a grid of identical cards. The whole row is clickable. On the home page every project appears in the contact sheet instead. |
| Project pages | Spec panel (Problem, Method, Testing, Result, Tools), then an annotated cover figure, then the write-up with numbered figures, then a gallery that supports video, then previous/next blocks. |
| Home | Navy hero: the name at display size, the two intro paragraphs and the facts (degree and graduation, availability, location, work authorization) in three columns, the three blocks, then the contact sheet: each published project as a text cell (title and result) followed by up to five of its pictures at one height, rows filled edge to edge. `sheet` in `project.json` picks the pictures; `short_title` shortens long titles everywhere but the browser tab. Then the featured project with the live scan, then "Skills and where to see them". No skill bars or ratings. |
| Live scan | ARC-001's per-angle medians (`scan.json`, from `scripts/export_scan.py`) drawn as a top view of the test scene with a scan-angle slider. The figure and its sentence are rendered at build time, so it reads fine without JavaScript; `assets/js/scan.js` only adds the slider. It labels two truths separately: the object on the beam's center line, and the nearest surface inside the ultrasonic beam. |
| Surfaces | Panels are separated by a tone step (white on canvas, sky for the spec panel), never by a 1px line or a shadow. Lines remain only in real tables, the resume's heading rules, and drawings. |
| Type scale | Five steps: 15 (small), 17 (body), 20 (lead), 24 (heading), and one large size per page (the home name at 7.5vw, page titles at 4.6vw up to 68px). |
| Motion | Three moves, all CSS keyframes on load, so nothing depends on a script and everything ends visible: the contact-sheet frames rise in with a 35ms stagger; on project pages the cover opens like a shutter (clip-path, 1.1s) while the photo settles from 1.12 scale, and the header, spec rows, list rows, and About text rise in reading order. Press feedback is `scale(0.97)` at 140ms. Reduced motion keeps short fades and drops all travel, scale, and the shutter. Curves: `--ease-out` (0.23, 1, 0.32, 1), `--ease-in-out` (0.77, 0, 0.175, 1). |
| Lessons | Optional `lessons` in `project.json` renders as "What I learned" at the end of the write-up. It must be Andrew's own words; never draft it for him. |
| Touch | Every `:hover` rule sits inside `@media (hover: hover) and (pointer: fine)`. Touch gets `:active` feedback, no tap highlight, and `touch-action: manipulation`. |
| Resume | Rendered on the page as a letter-size sheet that mirrors `Andrew_Miller_Resume_General.docx` (content and layout: bold title – context, bold date at the right), without the phone number. The PDF is printed from that same page, so the two always match. |
| Voice | Andrew's voice from his cover-letter style guide: complete first-person sentences, direct, active, factual, "hands-on" and iterative-testing language, a genuine learning orientation. No taglines, no hype, no bolded numbers. |
| Facts | Every number traces to `Andrew_Miller_Resume_General.docx`, `Master_Resume_Andrew_Miller.docx`, or the project's data; where they differ, the general resume wins on the site. Never invent motivation or results. |

## Avoid (AI-template tells)

- Tracked all-caps eyebrow labels. The resume headings are the exception, because the format guide asks for them.
- Middle-dot separators, and arrows appended to links.
- Identical card grids, gradient washes, and the same shadow on every surface. Only the resume sheet gets a paper shadow.
- Scroll-triggered reveals and blurred sticky headers. Entrances run once on load, never as you scroll.
- 1px outlined boxes and divider lines; separate with tone and space.
- Small labels above headings (eyebrows), including breadcrumbs above a page title.
- Bold accents on single numbers or words in previews.
- Placeholder or AI-generated imagery.

## Quality floor

- `python scripts/check_site.py` must pass before publishing. It checks every page at desktop and phone width, every link, every asset, alt text, headings, and horizontal overflow.
- Images have explicit dimensions and responsive WebP variants. Fonts are self-hosted. JavaScript is optional enhancement only: the Print button, `scan.js` (the scan slider), and `site.js` (plays the home clip unless reduced motion is on).
- Optional second gate: the design-taste-frontend inspector (`node <skill>/scripts/inspect.mjs <url>`). On the last run the home, Projects, ARC-001, and Bus pages had no FAILs. The Fan and About pages fail only its four-picture floor, which the photos in CONTENT_GAPS.md fix.
- Keyboard focus is visible (amber outline). Body text contrast is AA or better.
