# Design references: Rolex Finder (2026-11-17)

## Brief
- Whole site. Keep the look: green #0B2F23 left panel, cream #F6F2E8, gold #C9A348, Tienne + Inter.
- Audience: watch buyers and sellers, and employers or reviewers, equally.
- Include a small "how it works" section.
- Banned (CLAUDE.md): purple/blue gradients, glow, glassmorphism, emoji icons, centered hero with two buttons, identical card grids, AI-looking chips and eyebrows. Short dash only.

## Evidence
- Opened and measured, 1440 and 390 (screenshots in `design-refs/`): A Collected Man, Hodinkee, Phillips Watches, Fratello, Analog:Shift, Pl@ntNet, iNaturalist. Project: live site, home and results.
- Failed or blocked (bot check, 403): Chrono24, Watchfinder, Merlin Bird ID, Vivino, Rolex.com. Dropped.
- Awards actually seen on an award page: none. A search snippet lists Raymond Weil x Basquiat (Awwwards SOTD 2024-03-27) and IWC (2011) but I did not open those pages. All 7 references are "well regarded by feel and category", not "award winners".
- Colours are judged from screenshots. Cookie banners cover part of some first screens. One viewport size each.

## Measured table
| Site | H1 font | H1 size / weight | Body | Font sizes | Radii | Shadows | Gradients |
|---|---|---|---|---|---|---|---|
| A Collected Man | GT Alpina Fine | 66px / 300 | Helvetica Now 16 | 12 | 2px | 0 | 0 |
| Hodinkee | (none found) | - | Proxima Nova 16 | 13 | 2px, pill | 0 | 0 |
| Phillips Watches | DistinctDisplay | 28px / 400 | Montserrat 14 | 5 | 4px | 0 | 0 |
| Fratello | Tiempos Headline | 26px / 700 | Tiempos 16 | 13 | 3.75px, 32px | 1 | 1 |
| Analog:Shift | RightGrotesk | 48px / 700 | RightGrotesk 16 | 15 | 2px, 20px | 5 | 23 (photo overlays) |
| Pl@ntNet | PT Sans | 54px / 700 | PT Sans 16 | 12 | 6-18px | 3 | 1 |
| iNaturalist | Libre Baskerville | 43px / 700 | Lato 12 | 10 | 4-10px | 27 | 1 |
| **Rolex Finder** | Tienne | 64px / 400 | Inter 16 | 10 | 4, 16, 20px | 4 | 4 |

## Per-site notes (ranked by fit)
### 1. A Collected Man (watch dealer) - 11/14 (seen + measured)
- Light 300 serif at 66px, flat white, 2px radii, no shadows, no gradients. Hairline rules, sparse text. Product photo fills half the screen.
- Steal: light-weight large serif headline and text-only nav. Every watch gets one large photo, not a grid of boxes.
- Do not copy: black hero block, carousel.

### 2. Phillips Watches (auction house) - 11/14
- Five font sizes in total. Two columns: plain text left, one photo right. Upper-case tracked nav, 4px radii, no shadows.
- Steal: restraint (5 sizes) and the two-column "about" section with one real photo. Good model for the "how it works" section.
- Do not copy: long marketing paragraphs.

### 3. Pl@ntNet (identify tool) - 10/14
- Upload zone is the first thing on screen, on a tinted band, with one sentence. Results (known from product use, not opened here) show a reference photo per candidate.
- Steal: one-line instruction beside the drop zone. Candidate = photo + name.
- Do not copy: rounded green buttons, dashed box.

### 4. Fratello (editorial) - 9/14
- Serif headlines (Tiempos), black logo, small caps nav, hairline header. Cookie wall hides the rest.
- Steal: serif headline plus thin top rule. Not used for tools, only for tone.

### 5. iNaturalist (identify + community) - 8/14
- Serif H1, one photo hero, 5 icon features. 27 shadows measured.
- Steal: nothing structural. Shows what to avoid (icon grid).

### 6. Hodinkee (editorial) - 8/14
- Wide-tracked uppercase logo, white, centered nav, big photo. Ads dominate the first screen.
- Steal: tracked wordmark.

### 7. Analog:Shift (vintage dealer) - 7/14
- Dark photo hero, wrist shots, uppercase tracked nav, serif italic captions. 23 gradients are photo overlays.
- Steal: wrist photos give scale and trust. Italic serif caption.
- Do not copy: dark, photo-heavy, full-bleed hero (off-brief for a tool).

## Patterns across sites
- 5 of 7 use radii of 4px or less. 4 of 7 use zero shadows. Rolex Finder has 16 and 20px radii and 4 shadows.
- Watch sites use big photography and almost no UI chrome. Our results have no watch photo of the matches.
- 4 of 4 watch sites use a serif or a wide grotesk with uppercase tracked nav and no eyebrow labels over headings.
- Identify tools put the upload first and the reference photo next to every answer.
- Cookie walls and ads hurt every first screen. We have none, which is an advantage to keep.

## Project vs references
| Metric | Project | References |
|---|---|---|
| distinct font sizes | 10 | 5-15 |
| radii | 4, 16, 20px | 2-4px typical |
| shadows | 4 | 0-5 (iNat 27) |
| gradients | 4 (panel, gold button) | 0-1 |
| home section | eyebrow + headline + 3 numbered step cards with screenshots + 3 note cards | one sentence + one photo |
| results | 3 numbered cards, pills for references, "Match Score 94.73%", disclaimer box, red Remove button | ranked list with a photo each |

Template tells found in the project: eyebrow labels ("QUICK START", "PREDICTED ROLEX MODEL", "BEST RESULTS"), numbered 1-2-3 step cards, identical rounded card grids (twice), pill reference tags, 16-20px radii, gradient gold button, red Remove button, precise percentages that suggest more certainty than the model has.

## Ranked ideas
| # | Idea | From | Change | Impact | Effort | Conflicts |
|---|---|---|---|---|---|---|
| 1 | Results as a ranked list, not 3 cards | Phillips, A Collected Man | Top match large (name, reference numbers as plain text, one plain sentence). Others as hairline rows. No circles, pills or percent | High | Low | None |
| 2 | Reference photo per variant | Pl@ntNet, A Collected Man | One open-licence photo next to each candidate | High | High | Retailer photos are not licensed to show. Needs Wikimedia Commons or own photos. Cover 95 variants is a big job. Start with top 20 |
| 3 | Replace Quick Start cards with one line + short "How it works" | Phillips | Delete eyebrow and 3 numbered cards. Two columns: plain text left, one real result screenshot right. Include honest accuracy (71% on real photos, weak on Sea-Dweller vs Submariner) | High | Medium | Employer audience benefits. Keep text short |
| 4 | Flat shape system | A Collected Man, Phillips | Radii 2-4px only, no shadows, flat gold button, no panel gradient | Medium | Low | Green panel texture goes flat |
| 5 | Calmer controls | - | Replace/Remove become text actions, red button goes | Medium | Low | None |
| 6 | Confidence in words only | existing rule | Drop "94.73%". Show "Strong match" plus top-2 note when scores are close (Submariner vs Sea-Dweller) | Medium | Low | None |
| 7 | Cut type to 8 sizes, drop eyebrows | Phillips | Tokenise sizes | Low | Low | None |
| 8 | Wrist photo hero (one) in the green panel | Analog:Shift | One open-licence wrist photo for scale | Low | Low | Dark-photo trend, skip if it clashes |

## Do first / later
- Do first: 1, 3, 4, 5, 6, 7 (all front end, no new data, one push).
- Later: 2 (needs licensed photos, biggest payoff), 8.

## Open questions
1. OK to cover only top 20 variants with photos at first?
2. OK to show honest accuracy numbers on the page?
3. Which should I implement now?
