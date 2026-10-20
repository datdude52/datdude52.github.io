# Council brief: portfolio redesign

## Context
Andrew Miller is a 2nd-year mechanical engineering student at CU Boulder (4.0 GPA, Business minor, grad 2028). He's targeting aerospace and manufacturing internships. Background: three summers as a manufacturing technician, a fabrication internship (machining and welding), and a TA job. Projects:
- ARC-001: ultrasonic vs time-of-flight sensor characterization. 9,720 paired measurements, and a 4.5x angular-resolution gap explained from first principles with the Rayleigh roughness criterion. Has a real photo of a 3D-printed sensor fixture and radar-style scan plots.
- Cycloidal drive (SolidWorks plus 3D printed).
- Bus capacity tracker (sheet-metal enclosure, sensing, error below 2%).
- Reverse-engineered Honeywell fan (CAD and drawings).
- LangGraph AI agent (software).

Most projects have no photos yet. Expect phone photos, SolidWorks renders, drawings, and matplotlib or MATLAB plots.

The site is a static Python-generated site: home page (about, projects, resume), one page per project, and a resume PDF.

## Goal
The site should look like a real person made it with intent. Nothing should signal "AI-generated template." It should be simple and fast, and recruiters should be able to skim it in 30 seconds while engineers can still go deep.

## Current skeleton (which reads as AI-made)
- Inter body plus JetBrains Mono labels
- Tracked ALL-CAPS mono "eyebrow" labels above every heading
- Sticky nav with backdrop-blur
- Faint blueprint grid behind the hero
- Burnt-amber accent on warm off-white, with automatic dark mode
- Identical rounded cards with soft shadows and hover-lift, in an auto-fill grid
- Stat tiles with a left accent border
- Pill "chips" for tags, plus filter chips
- A middle dot (·) used as a separator everywhere

## Research findings
These are the documented "AI slop" tells as of 2026:
- **Type:** Inter (in about 47% of AI output); the Space Grotesk / Instrument Serif / Geist combos; a single serif italic accent word.
- **Color:** indigo or purple gradients; cream background with terracotta; dark background with acid green.
- **Layout:** a row of three identical rounded cards; badges above the H1; colored left or top card borders; stat-banner rows; numbered steps; tracked all-caps labels; middle dots; monospace data labels.
- **Chrome:** backdrop-blur sticky nav; fade-up-on-scroll animations; uniform py-20 spacing.
- **Copy:** generic phrasing like "seamlessly" or "Get started," and taglines that could belong to anyone.

What recruiters and hiring managers say they want:
- 3 to 7 projects, strongest first
- Lots of images with short captions, and annotated CAD or test images
- Each project's role, design intent, constraints and test numbers
- A scannable summary with depth available underneath
- Process shown, not just polished results
- No gimmicky animation, and no "look at my web-dev skills"

Performance:
- Self-host fonts. That removes the third-party round trip, worth about 180 ms of LCP.
- Two typefaces at most.
- LCP under 2.5 s and CLS under 0.1.

## Decisions to make
Pick one option per decision, or propose a better one. Give a one-line rationale for each.

**D1. Overall direction (the layout primitive)**
- A. **Technical-document / datasheet.** Strict grid, hairline rules, figure numbers ("Fig. 3"), and caption-driven pages, like a well-set engineering report or a McMaster-Carr page.
- B. **Editorial, photo-led.** Large images, generous margins, and project pages that read like a magazine feature.
- C. **Plain index.** A text-first home page that lists projects as rows (year, title, one-line result) with a small thumbnail, in the style of personal sites from researchers and engineers. Project pages are long-form with figures.
- D. Something else.

**D2. Typography** (self-hosted, at most 2 families)
- Option 1: a grotesk for both body and headings (e.g., "Instrument Sans", "Hanken Grotesk", "Public Sans" or "IBM Plex Sans").
- Option 2: a serif body for long-form reading (e.g., "Source Serif 4", "Newsreader", "Literata") with a sans for UI.
- Option 3: a technical humanist sans (e.g., "IBM Plex Sans", which has engineering heritage).
- Name the exact pairing you'd choose.

**D3. Color and theme**
- Light only, or automatic dark mode?
- Which accent: none (ink only, with link color), a single deliberate color tied to the subject (e.g., "engineering-drawing blue," "safety orange," "anodized aluminum blue"), or something else?

**D4. Home page order and project presentation**
- Order: about first, or projects first?
- Projects as cards in a grid, or as list rows?
- Keep the tag filter, or drop it, given there are only 3 to 6 projects?

**D5. What to cut.** List the elements of the current skeleton that should be removed outright.

**D6. The one bold move.** "Spend your boldness in one place." What is the single distinctive element this site should have?
