# Design decisions

Read this before changing anything visual or editorial.

- **Round 1** came from a four-advisor council: hiring manager, type designer, performance/accessibility engineer, and devil's advocate. The brief is in [council-brief.md](council-brief.md).
- **Round 2** (Oct 2026) added Andrew's direction: more color, links as blocks, real pages behind every link, the resume shown on the page, and copy written in his own voice.
- **Round 3** (Oct 19, 2026) came from research on what recruiters and hiring engineers screen for. It added the screening facts in the hero, skills linked to evidence, optional "What I learned" sections, and phone touch fixes. The open content list is [CONTENT_GAPS.md](CONTENT_GAPS.md).

## Principle

> The tell is assembling generic parts without content, not any single part.

Distinctiveness comes from real engineering evidence: photos of hardware, plots made from real data, annotated figures, and numbers. Styling isn't where it comes from.

## Current decisions

| Area | Decision |
|---|---|
| Pages | Home, Projects, a page per project, Resume, About, and 404. Every nav link is a real page. |
| Palette | Navy `#12284A` for the header, home hero, and footer bands. Drawing blue `#1F4E9C` for links, primary blocks, and figure annotations. Sky `#E8EEF8` for the spec panel and block hover. Canvas `#F3F5F8` page background with white panels. Ink `#1A1A1A`, muted `#55606E`. Burnt orange `#C2410C` appears only in plots, as the ultrasonic series. |
| Type | IBM Plex Sans, self-hosted, for the site. Carlito (metric-compatible with Calibri) for the resume sheet, matching the Word template. |
| Links | Calls to action are rectangular blocks with a 6px radius: primary (blue), default (white), and light/outline variants on navy. Nav links are blocks too, and the current page is filled white. Inline prose links stay underlined. |
| Projects | Shown as list rows (4:3 thumbnail plus text), not a grid of identical cards. The whole row is clickable. One featured project panel sits on the home page. |
| Project pages | Spec panel (Problem, Method, Testing, Result, Tools), then an annotated cover figure, then the write-up with numbered figures, then a gallery that supports video, then previous/next blocks. |
| Home | Hero intro, then a facts row (degree and graduation, availability, location, work authorization) because that is what a recruiter screens first. Featured project, project lists, then "Skills and where to see them", which reuses the spec panel and links each skill to its projects. No skill bars or ratings. |
| Lessons | Optional `lessons` in `project.json` renders as "What I learned" at the end of the write-up. It must be Andrew's own words; never draft it for him. |
| Touch | Every `:hover` rule sits inside `@media (hover: hover) and (pointer: fine)`. Touch gets `:active` feedback, no tap highlight, and `touch-action: manipulation`. |
| Resume | Rendered on the page as a letter-size sheet that follows `Resume_Format_Guide.docx`. The PDF is printed from that same page, so the two always match. |
| Voice | Andrew's voice from his cover-letter style guide: complete first-person sentences, direct, active, factual, "hands-on" and iterative-testing language, a genuine learning orientation. No taglines, no hype, no bolded numbers. |
| Facts | Every number traces to `Master_Resume_Andrew_Miller.docx` or the project's data. Never invent motivation or results. |

## Avoid (AI-template tells)

- Tracked all-caps eyebrow labels. The resume headings are the exception, because the format guide asks for them.
- Middle-dot separators, and arrows appended to links.
- Identical card grids, gradient washes, and the same shadow on every surface. Only the resume sheet gets a paper shadow.
- Fade-up scroll animations and blurred sticky headers.
- Bold accents on single numbers or words in previews.
- Placeholder or AI-generated imagery.

## Quality floor

- `python scripts/check_site.py` must pass before publishing. It checks every page at desktop and phone width, every link, every asset, alt text, headings, and horizontal overflow.
- Images have explicit dimensions and responsive WebP variants. Fonts are self-hosted. The only JavaScript is the inline Print button.
- Keyboard focus is visible (amber outline). Body text contrast is AA or better.
