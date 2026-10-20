## Overview

I designed an end-to-end pipeline that searches, filters, scores, and logs engineering internship postings. Everything it needs comes from a single YAML profile that holds my targets, experience, and standard form answers.

## How it works

The search step is a deterministic Python tool with adapters for nine job-board platforms, including Greenhouse, Lever, Workday, and USAJOBS, plus an HTML fallback. To cut out irrelevant postings, I added word-boundary title matching, exclusion families, and location tiers. Those filters narrowed 4,546 fetched postings to 14 relevant engineering internships.

The pipeline runs daily. An AI scoring step rates each posting's fit on a 1 to 5 scale and flags clearance and season constraints, then writes the results to a Notion tracker. Nothing is submitted automatically; every application goes through a human approval gate.
