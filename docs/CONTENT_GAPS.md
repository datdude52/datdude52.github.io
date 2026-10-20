# Content gaps: what to add, and where

This is the single to-do list for the site. It replaces `MEDIA_PLAN.md`. Every item says what is missing, what to shoot or write, and which file and field it goes in. The list is kept short on purpose. If something is not here, the site does not need it yet.

Last reviewed: October 19, 2026.

**Priority**
- **P1**: a reviewer will notice it is missing. Do these first.
- **P2**: makes a page noticeably stronger.
- **P3**: nice to have. Skip if time is short.

---

## Why these items (research summary)

Recruiters and hiring engineers look at a portfolio in two passes. The first pass is short, often well under a minute, and checks role fit, eligibility, and whether the best project looks real. The second pass happens before or during an interview, when an engineer reads one or two projects closely.

What the sources agree on:

1. **Show real hardware.** CAD screenshots and photos or videos of physical builds are the baseline ask. Photos of builds add credibility that renders do not.
2. **Problem before solution.** Each project should state the problem, your actions, and then the result, instead of jumping to the finished product.
3. **Your role on team projects.** Say exactly what you did and what the team did. Claiming group work without that is a common red flag.
4. **Challenges, iterations, and failures, with what you learned.** Several sources ask for this directly. Interviewers also ask about failures to see how you handle them.
5. **Quantified results.** Numbers give a reviewer a sense of scale.
6. **Eligibility up front for aerospace and defense.** Many aerospace roles are gated by ITAR U.S.-person rules, graduation date, and enrollment after the internship, so those facts should be easy to find.
7. **Fewer, better projects.** Three to seven projects, best first, in a consistent format. Three well-documented projects beat seven thin ones.
8. **Easy to navigate, fast, current.** A clear menu, the resume one click away, and recent work.

Sources: [BU College of Engineering, Key Factors of Engineering Portfolios](https://www.bu.edu/eng/files/2025/04/Key-Factors-of-Engineering-Portfolios.pdf); [Trossen Robotics portfolio guidelines](https://www.trossenrobotics.com/portfolio-guidelines); [Duke Career Hub on online portfolios](https://careerhub.students.duke.edu/blog/2021/08/20/communicate-your-experiences-with-an-online-portfolio-elevate-your-impact-using-this-job-seeking-tool/); [Vista Projects on ME portfolio structure](https://www.vistaprojects.com/mechanical-engineering-portfolio-examples/); [Indeed, mechanical engineer interview questions](https://www.indeed.com/career-advice/interviewing/interview-questions-mechanical-engineer); [Extern guides to Sierra Space](https://www.extern.com/post/sierra-space-internship-guide), [RTX](https://www.extern.com/post/rtx-internship-guide), [Relativity Space](https://www.extern.com/post/relativity-space-internship-guide) and [Honeywell Aerospace](https://www.extern.com/post/honeywell-aerospace-internship-guide) internships; [InterviewPal resume review timing study](https://www.interviewpal.com/blog/how-long-recruiters-actually-spend-reading-your-resume-data-study); [Data Engineer Academy on skimmable portfolios](https://dataengineeracademy.com/blog/how-to-build-a-data-engineering-portfolio-recruiters-can-skim-in-60-seconds/). Most of these are career-center and industry guides, not controlled studies, so the advice above sticks to what several of them agree on.

---

## Already done in this round

- **Home page facts.** Degree and graduation date, availability, location, and U.S. citizenship now sit under the intro. They come from `profile.yaml`. Edit them in `content/site.json` → `home.facts`.
- **Skills and where to see them.** A short section at the bottom of the home page lists four skill areas from the resume, and each one links to the projects that show it. Edit in `content/site.json` → `home.skills`.
- **"What I learned" sections.** Any project can now have a `"lessons"` field in `project.json`. It shows as a "What I learned" section at the end of the write-up, and only when you have written it. None are filled in yet, because they have to come from you (see P1 items below).
- **Honeywell drawing moved up.** The dimensioned, toleranced drawing sheet is now the first gallery figure, and its caption says what it shows.
- **Social preview image.** Links shared on LinkedIn or in email now show the ARC-001 fixture photo (`content/images/og.jpg`) once the site has its live address.
- **Phone fixes.** Hover effects only apply with a mouse, taps give immediate feedback, and the blue tap flash is gone. Check these on your phone once the site is live.
- **"Last updated" date** in the footer, so a reviewer can see the site is current.

---

## The short list (do these in order)

| # | Item | Pri | Where it goes |
|---|---|---|---|
| 1 | Put the live site URL on your resume and LinkedIn | P1 | Master resume header, `content/resume.json` → `contact`, LinkedIn Featured |
| 2 | ARC-000: photo of the original scanner hardware | P1 | `arc-000-ultrasonic-scanner` |
| 3 | ARC-001: wide photo of the full test scene | P1 | `arc-001-ultrasonic-vs-tof` |
| 4 | "What I learned" for ARC-001, ARC-000, and Bus Tracker | P1 | `"lessons"` in each `project.json` |
| 5 | Bus Tracker: team size and who did what, plus how 98% was measured | P1 | `bus-capacity-tracker/project.json` → `spec` |
| 6 | Desk: photo of the finished desk | P1 | `small-builds` |
| 7 | Internship Pipeline: one screenshot for the cover | P1 | `internship-search-pipeline` |
| 8 | Honeywell Fan: real parts on a table with calipers | P2 | `honeywell-fan-reverse-engineering` |
| 9 | Home and About: a photo of you working in a shop or lab | P2 | `content/images/about.jpg` |
| 10 | ARC-001: link the final report PDF when it is done | P2 | `arc-001-ultrasonic-vs-tof/project.json` → `links` |

Everything below gives the exact details for each item.

---

## Site-wide

### 1. Use the live address everywhere (P1)
- The site is published at https://datdude52.github.io (set in `content/site.json` → `base_url`).
- Add it to the contact line of `Master_Resume_Andrew_Miller.docx`, then copy that line to `content/resume.json` → `contact` and run `python scripts/build.py --pdf`. Check the PDF is still one page.
- On LinkedIn, add it under **Contact info → Website** and as a **Featured** link with the ARC-001 page.

### 2. Make the scanner code public, or leave it off (P3)
- `github.com/datdude52/sonar-scanner` is private. If you make it public, add `{ "label": "Code on GitHub", "url": "https://github.com/datdude52/sonar-scanner" }` to `links` in both the ARC-000 and ARC-001 `project.json` files. Add a short README to the repo first, because a reviewer who clicks through will read that before the code.

### 3. Things not to add
These came up in the research or in common portfolio templates, and they would make the site worse:
- **Skill bars or percentage ratings.** Nobody trusts them, and the skills section already links to evidence instead.
- **A blog, testimonials, or a "services" page.** They are not what an internship reviewer is looking for.
- **More than six published projects.** Publish a draft only when it meets its bar below, and consider retiring Desk and Chess Set to the About page once the cycloidal drive is live.
- **Separate pages for Fiberlok and Hueber.** The resume covers them. Do not post photos from either shop without the company's OK.
- **A downloadable PDF portfolio.** The site and the one-page resume already cover it.

---

## Home page (`content/site.json`)

### Hero photo (P2)
- **Now:** you in front of the Trevi Fountain. It is a good photo of you, but it says travel, not engineering.
- **Shoot:** you at a workbench, printer, mill, or the FSAE shop, working on something, looking at the work rather than the camera. Waist up, landscape or square, daylight from the side. A plain or tidy background.
- **Where:** replace `content/images/about.jpg` (the build crops it to a 4:5 portrait for the About page and uses it in the home hero). Update `about.photo_alt` to describe the new photo, for example "Andrew Miller adjusting a 3D-printed sensor fixture at his desk".
- If you shoot this, keep the Trevi photo for the About page by saving it as a second file and asking me to add a second About photo.

### Facts row (check, no action needed)
- Confirm these are how you want to present yourself: "Summer 2027, May to August", "Boulder, Colorado", "U.S. citizen". If you want to state that you only want roles on the Front Range, add a row `["Location preference", "Colorado Front Range"]`.

---

## Projects

### ARC-001: Ultrasonic vs. Time-of-Flight (`content/projects/arc-001-ultrasonic-vs-tof/`)
This is the featured project, so it gets the most attention.

| Item | Pri | Exact description | Where |
|---|---|---|---|
| Full test scene | P1 | Wide shot from above at about 45°. The rig at the near edge of the frame, all six objects in their measured positions behind it, a tape measure laid out from the sensor toward the objects for scale. Landscape, daylight, clear the bed and desk clutter out of frame. | `images/test-scene.jpg`, then in `writeup.md` under "Test rig", after the second paragraph: `![Overhead view of the test scene with the rig in front and six objects placed behind it.](images/test-scene.jpg "The six-object test scene. Each object was measured into coordinates for the ray-cast ground truth.")` |
| Rotated box failure case | P2 | Close-up of the box turned about 45° to the sensor, with the fixture in frame pointing at it. | `gallery`, caption ending with the +223 mm error |
| Bracket CAD next to the print | P2 | SolidWorks render of the coaxial bracket on the left, the printed bracket photographed from the same angle on the right, on a cutting mat. Combine into one image. | `gallery` |
| One-sweep video | P2 | 10 to 15 seconds, landscape, phone propped up. The servo sweeping with the laptop plotting live behind it. No talking needed. | `python scripts/prepare_video.py IMG_xxxx.MOV content/projects/arc-001-ultrasonic-vs-tof/images/sweep`, then add to `gallery` |
| "What I learned" | P1 | Two to four sentences in your words. Questions to answer: What did the dry runs teach you about collecting data before you trust it (the 12 defects, the −38 mm bias)? What would you do differently in the next test plan? | `"lessons": ["…"]` in `project.json` |
| Final report | P2 | When the report is done, export a PDF. | Save as `images/ARC-001_Report.pdf` and add `{ "label": "Read the report (PDF)", "url": "images/ARC-001_Report.pdf" }` to `links`. Remove `"progress"` at the same time. |

### Bus Capacity Tracking System (`content/projects/bus-capacity-tracker/`)
| Item | Pri | Exact description | Where |
|---|---|---|---|
| Team and role | P1 | One sentence on team size and what teammates owned, so your part is clear. For example: "Team of four. I led design and manufacturing; teammates owned the IR circuit and the counting code." Use the real split. | New `spec` row `["Team", "…"]` right after `My role` |
| How 98% was measured | P1 | How many walk-throughs per trial, how a miss and a double count were scored, and how many design iterations. | New `spec` row `["Testing", "…"]` before `Result` |
| Doorway demo video | P1 | `Cowtools/Video/IMG_1065.MOV`, the best demo you have. It shows teammates' faces, so get their OK first. | `python scripts/prepare_video.py ".../IMG_1065.MOV" content/projects/bus-capacity-tracker/images/doorway-demo`, add to `gallery` as the first item |
| Flat pattern or drawing | P2 | Export one SolidWorks Sheet Metal flat pattern or drawing sheet with bend lines as a PNG (File → Save As → PDF, then screenshot at full resolution). | `gallery`, after the display housing CAD |
| Accuracy over iterations | P2 | If the trial log still exists, a simple bar chart of detection error for each design iteration. | `gallery`, or ask me to build the chart from the log |
| "What I learned" | P1 | What did leading design and manufacturing on a team teach you? Which design change fixed the most error? | `"lessons"` |

### ARC-000: Ultrasonic Sonar Scanner (`content/projects/arc-000-ultrasonic-scanner/`)
This is the only published hardware project with no photo of hardware.

| Item | Pri | Exact description | Where |
|---|---|---|---|
| The scanner itself | P1 | The original scanner on its desk clamp, shot from the front at sensor height so the HC-SR04 "eyes" face the camera. Landscape, plain wall behind. | `images/scanner.jpg`. Make it the cover (`"cover": "images/scanner.jpg"`), and move the current radar plot `images/cover.png` to the first `gallery` item. |
| Shroud lineup | P1 | The printed shrouds laid out shortest to longest on a cutting mat, a ruler along the bottom edge. This shows the iteration in one picture. | `gallery`, caption naming the lengths |
| Clamp iterations | P3 | Dovetail clamp next to the threaded-spindle clamp. | `gallery` |
| "What I learned" | P1 | What did isolating one variable at a time teach you, and why did you decide to characterize the sensors instead of just swapping them? | `"lessons"` |

### Reverse-Engineered Honeywell Fan (`content/projects/honeywell-fan-reverse-engineering/`)
| Item | Pri | Exact description | Where |
|---|---|---|---|
| Real parts with calipers | P2 | If you still have the fan: the disassembled parts laid out on a table, calipers on one part. This proves the model came from real measurements. | `gallery`, first item |
| Cleaner drawing export | P2 | The current drawing is a screen capture with SolidWorks toolbar icons across the top, and the title block description overlaps. Re-export the sheet from SolidWorks (File → Save As → PDF, then convert to PNG at 200 dpi) and fix the overlapping description text. | Replace `images/drawing.png` with the same name |
| Measurement detail | P3 | One sentence in the write-up on the hardest feature to measure and how you got it, if you remember. | `writeup.md` under "Process" |

### Desk and Magnetic Chess Set (`content/projects/small-builds/`)
| Item | Pri | Exact description | Where |
|---|---|---|---|
| Finished desk | P1 | The desk in your room, whole desk in frame, shot from a front corner at about desk height. Clear the top first. | `gallery`, first item. The desk has only a render now. |
| Desk details | P2 | Wood species, overall dimensions, and the joinery you used. One sentence. | `spec` → `Desk` row |
| Magnet close-up | P2 | A piece turned over showing the magnet in its base. | `gallery` |
| Full set | P3 | All pieces lined up on a plain background. | `gallery` |

### Internship Search Automation Pipeline (`content/projects/internship-search-pipeline/`)
| Item | Pri | Exact description | Where |
|---|---|---|---|
| Cover screenshot | P1 | The Notion tracker with scored postings. Crop out any personal notes and anything you would not want a recruiter to see, such as company names you rejected. | `images/cover.png`, `"cover": "images/cover.png"` with `cover_alt`. Without it, this is the only text-only row on the site. |
| Pipeline diagram | P2 | profile.yaml → search adapters → filters → AI scoring → Notion → human approval. Ask me to draw it. | `gallery` |

---

## Drafts (hidden until they meet the bar)

Build with `python scripts/build.py --drafts` to see them.

| Project | Publish when | Photos to get |
|---|---|---|
| Two-Stage Cycloidal Drive | The write-up has the reduction ratio and a test result (even "the output turned at the expected ratio"), and you have #1 and #2 below. | 1. Exploded render (SolidWorks: Exploded View, then File → Save As → PNG). 2. Printed parts laid out in assembly order. 3. 10-second video of the input and output turning, with tape on the output so the reduction is visible. 4. Close-up of the disk meshing with the roller pins. |
| Camera-Tracking Gimbal | It tracks something on video. | 1. CAD render of the camera stage and fixed base. 2. Photo of the CSI ribbon routing through the axes, with callouts. 3. Video of the gimbal following a moving object. |
| Internship Application Agent | Consider folding it into the Pipeline page as one section instead of a separate page, so the site does not have two AI-tool projects next to its mechanical work. | Graph diagram and one example output. |

## FSAE (no page yet)
- Leave it on the resume and About page for now.
- Once you own a specific part or test (a CAD part, a bracket, a harness, a test result), add a project page for that piece of work, not for the team. Check the team's media rules before posting car photos. `Camera Roll/Me_FSAE.jpg` is a social photo with someone else in it, so do not use it.

---

## How to shoot so it looks right on the site

- **Light:** daylight near a window, or two desk lamps from the sides. Not the overhead light alone.
- **Background:** plain wall, cutting mat, or poster board. Move clutter out of frame.
- **Framing:** landscape (4:3) for covers and test shots. List thumbnails are cropped to 4:3.
- **Scale:** a ruler, calipers, or a hand in at least one shot per project.
- **Video:** 5 to 15 seconds, landscape, phone steady, no talking. Then run `scripts/prepare_video.py`.

## How to add a photo

1. Drop the file in `content/projects/<slug>/images/`.
2. Add it to `gallery` in that project's `project.json` with `alt` (what is in the picture) and `caption` (what it shows and why it matters), or reference it in `writeup.md` as shown above.
3. Run `python scripts/build.py`, then `python scripts/check_site.py`.
4. Commit and push. The site rebuilds and publishes on its own.

## Photos already on the site

These are done and do not need action. Source files are listed so they can be found again.

- **ARC-001:** fixture cover with callouts (`Sonar Scanner/Sensor_fixture.jpg`), polar overlay and resolution ladder (generated by `CODE/analysis/portfolio_figures.py`).
- **Bus Tracker:** display cover (`Cowtools/Pictures/IMG_0885.HEIC`), transmitter, transmitter electronics, emitters, display housing CAD, LED panel, schematic, display top, display demo video (`Cowtools/Video/IMG_0913.MOV`). Do not use `GEEN 1400/Final Project/Bus_Stop_Sign.jpg`; it looks AI-generated.
- **ARC-000:** ultrasonic and time-of-flight radar sweeps (`Sonar Scanner/Visualization/`).
- **Honeywell Fan:** exploded render, rear render, drawing sheet.
- **Desk and Chess Set:** board held upside down, desk CAD.
- **About:** `Pictures/Camera Roll/EngProjAboutMePhoto.jpg`.
