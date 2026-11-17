# Rolex Finder needs proof, context and speed

Rolex Finder has one real edge over the market: it is a free, no-signup web tool that shows honest uncertainty, while most competitors are iPhone apps behind paywalls or scan quotas. But today it reads as a model demo, not a product. The result is a probability table plus Google Images links, there is **no accuracy number anywhere in the repo**, the cold start is about 40 s with no real progress feedback, and failures show a blank screen. Competitors win on **context** (reference number, years, specs, price range, listings) and on **feedback loops** (one-tap "wrong match" reports), not on visibly better AI, and their accuracy claims are unverified vendor marketing. For employers, the biggest gain is cheap: publish a held-out benchmark and a model card, add working loading, error and low-confidence states, and ship pre-computed example results so a recruiter never waits on a cold server. For casual buyers and collectors, the biggest gain is a "watch detail" page per reference. Do not add "real or fake" verdicts. The fixes below are ranked by impact against effort, and the screen sketches in section 5 show the finished site.

## How the market compares, and why it feels more complete

The category is crowded but shallow. Chrono24's app has a scanner built into the home screen and returns market value, full reference number, case material, production years and listing links ([WatchGecko](https://www.watchgecko.com/blogs/magazine/the-new-chrono24-watch-scanner)). WatchCharts shows reference market price, a 1-year trend, for-sale links and a one-tap wrong-match report ([WatchCharts](https://watchcharts.com/identify)). Grailr is a web tool covering about 30 brands, and it explains its reasoning and states plainly that confidence is not accuracy and identification is not authentication ([Grailr](https://grailr.watch/identify)). WatchScanning takes up to 4 photos (dial, caseback, bezel, bracelet) and adds reasoning per visible cue ([WatchScanning](https://www.watchscanning.com/identify-watch-from-photo/)). watchID is an iPhone app with scan history and a community tab ([App Store](https://apps.apple.com/us/app/watch-id/id6478837777)). Most paywall: WatchSnap charges $7.99/week or $39.99/year ([App Store](https://apps.apple.com/app/id6761362953)), Grailr gives 2 lifetime free checks, and watchID prices Pro at $2.99/week.

| Product | Input | Output beyond the name | Honesty about uncertainty | Cost |
|---|---|---|---|---|
| Chrono24 scanner | App, camera or upload | Price, ref, years, listings | Opaque | Free |
| WatchCharts | iPhone/Android app | Price, 1-yr trend, listings, wrong-match report | Not shown | Free in app |
| Grailr | Web | Specs, value range, reasoning | Explicit | 2 free lifetime checks |
| WatchScanning | Web, up to 4 photos | Reasoning, value range, PDF report | Flags weak inputs | First scan free |
| WatchSnap, WatchLens, clones | iPhone | Value, portfolio, authenticity verdict | Weak, risky claims | Weekly or annual subscription |
| Watchbase | None (catalogue) | Specs, calibres | n/a | Free, restricted reuse |
| **Rolex Finder today** | Paste or browse | Probability table, 3 variant cards, Google links | Raw 4-decimal percentages, no warnings | Free, no signup |

Why competitors feel better: they answer the next question. A person who learns "Submariner" immediately asks "which reference, how old, what does it cost?" Chrono24 and WatchCharts can answer because they own listings and sales data, a moat a portfolio project cannot copy. The notes also found that Rolex Finder's own differentiators are real. A free, web-based, no-signup, Rolex-focused tool is a gap, since the strong options are phone apps or quota-limited. No verified competitor shows a **ranked top-3 with probabilities**, a "why this match" view, or a "similar references and how to tell them apart" block. Grailr and WatchScanning come closest through text reasoning. That is where Rolex Finder should lead.

Content bar for the "learn more" page: strong reference pages combine a table of references with years, case, calibre and dial, nickname origin, history, price as median plus range with an "as of" date, buyer-type advice and an FAQ ([Bob's Watches](https://www.bobswatches.com/rolex-blog/buying-guides/rolex-gmt-pepsi.html), [Sotheby's](https://www.sothebys.com/en/articles/the-rolex-gmt-pepsi-the-key-references)). Pages also need a "discontinued" status, since the steel Pepsi 126710BLRO was reported discontinued on April 1, 2026 (both sources above).

## What the site does well, and what breaks today

Done well, from the repo audit: a clear two-panel layout (dark green upload, cream result), a tutorial panel for first-time users, a health ping on page load that starts waking the server early, session persistence of the last result, and a two-stage idea (family, then variant) that fits how Rolex references work. The pipeline detects the watch, straightens the bracelet, crops the dial, classifies the family with EfficientNet-B0, then ranks variants with CLIP.

What breaks, in order of how much it hurts credibility:

**Trust and honesty.** The repo stores **no accuracy figure, confusion matrix or per-class metric**; `evaluate.py` only prints overall test accuracy. The variant "Match Score" is a CLIP softmax over hand-written text prompts and has never been evaluated, yet the UI shows it as a percent next to reference IDs. The classifier always returns some Rolex family, so an Omega gets labelled as a Rolex with a confident number. The UI shows probabilities to 4 decimals ("99.8213%", "0.0003%"), which is fake precision. The backend returns a `variant_status` field to flag weak matches, but the front end ignores it and always says "Closest known matches".

**Dead ends and silent failure.** Any failed request, including a corrupt image or a timeout, calls `onPrediction(null)` and shows the tutorial again with no message. A "no watch detected" result renders as "Confidence 0.00%", three cards named "None", and a 15-row table of zeros. There is no timeout or cancel. The README promises drag-and-drop, but the code only has paste and browse, and `react-dropzone` is installed but never used.

**Loading.** The wait is a button label ("SCANNING...") plus a static note. Nielsen's research puts the attention limit at 10 s and recommends percent-done feedback for longer waits ([NN/g](https://www.nngroup.com/articles/response-times-3-important-limits/)), and the progress bar must never stall, lie or reset ([UX Tigers](https://www.uxtigers.com/post/progress-indicators)). The tutorial says "a few seconds" while the upload box says "up to 40s".

**Polish bugs a recruiter will see.** The same class is spelled two ways on one screen ("Gmt-Master" in the header, "Gmt Master" in the table; real names are GMT-Master, Turn-O-Graph, Air-King). The nav bar is fixed and transparent, so scrolled text slides under it. The viewport is set to 80% initial zoom. Tutorial cards expand on hover, which fails on touch. There is almost no accessibility support (no `aria-live` for status, no keyboard path on the drop zone, no reduced-motion handling). The page title is just "Rolex Finder" with no meta description or social preview. The README says 15 families and a 180 s scaledown; the code has 14 and 1200 s.

**Use case.** Output stops at a family name and Google Images links. Variant cards list several reference IDs (for example five for one Air-King variant) with no explanation of which differs, so the user must leave the site to learn anything.

## Fixes ranked by impact against effort

Work top to bottom. Items 1 to 6 are mostly front end and content, take days not weeks, and carry most of the "looks professional" value.

| # | Fix | Why it matters | Effort | Impact |
|---|---|---|---|---|
| 1 | Benchmark + model card in README and a `/model-card` page | Employers check metrics first; competitors publish none, so honest numbers stand out | Medium | Very high |
| 2 | Real loading, timeout, error and no-watch states | Today failures look like a broken site | Low | Very high |
| 3 | Pre-computed example photos with stored results | Recruiter sees a full result in under 1 s, cold start or not | Low | Very high |
| 4 | Low-confidence and "not a supported Rolex" states; stop showing 4-decimal numbers | Removes fake precision and false Rolex labels | Medium | High |
| 5 | Watch detail page per variant (specs, years, status, nicknames, how to tell apart, links) | Answers "I want to know more"; main gap vs competitors | Medium | High |
| 6 | Fix polish bugs: names, nav, zoom, hover-only tutorial, drag-and-drop, titles, README | Cheap credibility | Low | Medium |
| 7 | Show the cropped image the model used, with "wrong? tell us" feedback | Builds trust, collects labelled failures | Low to medium | Medium |
| 8 | Image preprocessing fixes (section 4) | Accuracy gain on real phone photos | Medium | High, unmeasured |
| 9 | Reference-image retrieval for variants and a search box | Replaces untested CLIP text prompts and Google links | High | High |
| 10 | Cold-start cuts (section 4) | Smaller first-visit wait | Medium | Medium |
| 11 | Other brands (Omega, Tudor) | Realism, but data is scarce and legally murky | Very high | Defer |

Skip authenticity verdicts entirely. Practitioner sources say photo-only authentication is unreliable and in-person caseback or movement inspection is definitive ([SwissWatchExpo](https://www.swisswatchexpo.com/thewatchclub/how-to-spot-a-fake-rolex/)). WatchSnap offers a "Likely Genuine" verdict and carries the liability. A visible "identifies models, does not authenticate" line is a strength. Also add an "unofficial, not affiliated with Rolex" notice: using the name to identify products is generally defensible, while implying endorsement is the real risk ([Fashion Law](https://www.thefashionlaw.com/rolex-resale-fight-tests-limits-of-trademark-power-in-the-luxury-watch-market/)). Not legal advice. Copy no Rolex.com photos or text, whose terms restrict reuse ([Rolex terms](https://www.rolex.com/en-us/legal-notices/terms-of-use.html)).

## Better search and image preprocessing

**What "search" should mean.** Today it is a client-side Google Images link per reference ID. Three cheap upgrades fit a dataset under 100K vectors, where exact flat search is enough and no vector database is needed ([Zilliz](https://zilliz.com/learn/choosing-right-vector-index-for-your-project.md)). First, **visual search**: embed reference photos with a frozen model (DINOv2 or SigLIP 2) and return the nearest references within the predicted family. Frozen-embedding prototypes beat classifiers trained on small in-domain sets in a fine-grained few-shot study ([arXiv 2408.13632](https://arxiv.org/pdf/2408.13632)), and adding a new reference needs 5 to 20 photos, not retraining. No head-to-head watch benchmark exists, so test it against the current CLIP prompts before switching. Second, **text search** over a reference and nickname table ("Hulk", "Pepsi", "116610LV") using client-side fuzzy search. Third, **filters** by family, size, material and era over the same table. A reference-number decoder (last digit gives metal, suffix gives bezel colour) is a cheap sanity check on model output, though sources disagree on some digit rules and it works best on dress models ([LuxuryBazaar](https://www.luxurybazaar.com/grey-market/rolex-reference-numbers/)).

**Where the current accuracy is probably lost.** These are inferences from reading code, not measurements. Training used only product photos from one retailer (swisswatchexpo), while users upload wrist photos, and the dial-crop pipeline applied at inference was never applied to training images, so the model sees different inputs in training and use. Classes are lopsided: Datejust has 6,457 training images (about 37%) and Milgauss 136, roughly 47 to 1, with no class weighting. The inference transform squashes the crop to 224 by 224 instead of preserving aspect ratio. Specific code bugs: the dial box uses `y2 = y1 + width` instead of height; phone photos are never EXIF-rotated, so sideways uploads reach the model; the PCA bracelet rotation cannot tell 0 from 180 degrees, so a watch may be turned upside down; and rotation fills corners with black. Long CLIP prompts probably exceed the 77-token limit, so their tails are cut (unverified per entry).

**Preprocessing plan, cheapest first.** Fix EXIF orientation, the `width` bug and the 180-degree ambiguity. Resize large phone photos in the browser before upload, which also cuts upload time. Add quality gates with plain messages: short side under 224 px, blur via Laplacian variance (threshold must be tuned on your own sharp and blurry samples, [PyImageSearch](https://pyimagesearch.com/2015/09/07/blur-detection-with-opencv/)), and no detection. Run the same crop pipeline on training images, or train with some background kept so crop errors do not hurt. Use multi-crop or multi-scale test-time augmentation and avoid horizontal flip, which breaks dials, text and crown side (my inference; no source found). SAM 2 masks are optional: the notes found no source showing mask crops beat box crops for classification, and SAM 2 adds latency and GPU cost ([PMC12694221](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12694221/)). Adopt it only if your A/B test shows a gain. Grounding DINO is good at "find the watch", but open-vocabulary detectors struggle with fine-grained class differences ([arXiv 2504.07252](https://arxiv.org/pdf/2504.07252)), so keep the classifier for "which watch".

**Honesty layer.** Fit a temperature on a held-out split, show top-3, and add a separate out-of-scope score (energy or max-logit, [arXiv 2010.03759](https://arxiv.org/pdf/2010.03759)). Calibration and out-of-scope detection must be evaluated separately, and open-set calibration error is far worse than closed-set (0.230 against 0.011 in one study, [arXiv 2205.07160](https://arxiv.org/pdf/2205.07160)). Use four states: High, Medium (show top-3), Low ("not sure, retake the photo") and Out of scope ("does not look like a supported Rolex"). Choose thresholds using non-Rolex negatives such as Omega, Tudor and non-watch images. A multimodal LLM fallback is optional; specialist models beat general LLMs at fine-grained classification ([arXiv 2507.01955](https://arxiv.org/pdf/2507.01955)), so call one only on Low confidence, constrained to the top-3, and label it "AI description, not verification".

**Cold start.** Modal names two causes: container queueing and first-call initialisation like loading weights ([Modal guide](https://modal.com/docs/guide/cold-start)). The repo loads three models (Grounding DINO base, EfficientNet-B0, CLIP B/16) and has no per-phase timing, so add timing logs first. Options, cheapest first: keep the page-load ping and add a "Server warming up" chip; ship pre-computed examples (item 3); run Grounding DINO in fp16 or swap to a smaller detector; drop the unused `steps` base64 images from the response; try Modal memory snapshots (GPU snapshots are alpha, and gains are small if most time is weight loading, [Modal docs](https://modal.com/docs/guide/memory-snapshots)). Always-warm costs: about $29 per month for 0.5 CPU core plus 2 GiB by my arithmetic from [Modal pricing](https://modal.com/pricing), versus roughly $430 per month for a T4, which does not fit the $30 free credit. So warm-24/7 only works with a small CPU model, for example ONNX with int8. Also check the Render layer: free web services spin down after 15 minutes and take about a minute to wake ([Render docs](https://render.com/docs/free)). The live site serves a static bundle and calls Modal directly, so this may not apply, but the repo does not show Render's service type. Static hosting (Cloudflare Pages, Netlify) removes the question. Also set `max_containers` above 1: with `max_inputs=1` a shared link queues every visitor.

## The improved site, screen by screen

All sketches use placeholder wording. Photos shown in the result come from your own or openly licensed images.

**1. Landing.** One screen, one job: upload or try an example. Examples load instantly from stored results.

```
+--------------------------------------------------------------+
| Rolex Finder         Identify | Models | How it works | About |
+--------------------------------------------------------------+
|                                                              |
|   Identify a Rolex from a photo.                             |
|   Free. No signup. Unofficial - not affiliated with Rolex.   |
|                                                              |
|   +--------------------------------------------+   Engine:   |
|   |   Drop a photo here, paste (Ctrl+V),       |   (o) Ready |
|   |   or [ Choose photo ]  [ Take photo ]      |   or        |
|   |   Tip: dial facing you, sharp, good light  |   (.) Warm- |
|   +--------------------------------------------+   ing up    |
|                                                              |
|   No photo handy? Try an example:                            |
|   [Submariner] [Datejust] [Daytona] [GMT-Master]             |
|   (instant, pre-computed - "Run live" also available)        |
|                                                              |
|   Reported accuracy: Top-1 xx% | Top-3 xx%  (held-out set)    |
|   [See benchmark and limits]                                 |
+--------------------------------------------------------------+
```

Why: the example row guarantees a recruiter sees a full result in under a second. The accuracy line, once measured, is the single strongest professional signal. The status chip turns the wait into information. After upload, a crop-and-rotate preview with a "Looks right? Identify" button catches bad photos before they cost 40 s.

**2. Loading (first visit, cold server).** Tied to real phases, never stalling, with a timeout and retry.

```
+--------------------------------------------------------------+
|  [your photo, dimmed]                                        |
|                                                              |
|  Step 2 of 4: Loading the models      00:23 elapsed          |
|  [=================>............]                            |
|  (x) Photo received   (x) Server awake                       |
|  (>) Loading models   ( ) Reading the dial                   |
|                                                              |
|  First visit can take up to a minute while the server wakes. |
|  Later scans take a few seconds.                             |
|  [ Cancel ]            Browse the model guide while you wait |
+--------------------------------------------------------------+
After 90-120 s:  "Taking longer than usual. [Retry] [Try an example]"
```

Why: guidance above says a bar must not stall or reset and may show an approximate time. Phases need to come from the backend (status endpoint or streamed events), or the bar should ease to about 90% and wait. Offering reading material during the wait turns dead time into the model-guide traffic.

**3. Result.** One clear answer, honest alternatives, and a path to learn more. The same pattern appears in reference apps: ranked list, most similar reference image per candidate, feedback. Pl@ntNet does this ([API docs](https://my.plantnet.org/doc/api/identify)), and Merlin's tool put the right species in its top 3 about 90% of the time in its own tests ([eBird](https://ebird.org/news/merlinid)).

```
+--------------------------------------------------------------+
| [Your photo] -> [What the model saw: cropped dial]           |
|                                                              |
|  Best match: Rolex Submariner Date (modern)                  |
|  Confidence: HIGH  [########--]   Family 94%                 |
|  Likely references: 126610LN | 126610LV                      |
|  Status: current | Years: 2020-present                       |
|  [View model page]   [Compare with alternatives]             |
|                                                              |
|  Other possibilities                                         |
|  +----------------+ +----------------+ +----------------+    |
|  | ref photo      | | ref photo      | | ref photo      |    |
|  | Sub no-date    | | Hulk 116610LV  | | Sea-Dweller    |    |
|  | 3%  How to     | | 2%  How to     | | 1%  How to     |    |
|  | tell apart     | | tell apart     | | tell apart     |    |
|  +----------------+ +----------------+ +----------------+    |
|                                                              |
|  Not right? [Wrong match] -> pick the correct model          |
|  Identifies models only. Does not authenticate watches.      |
|  Search: [ref or nickname............] [Find similar looks]  |
+--------------------------------------------------------------+
```

Low-confidence variant: banner "Not sure. Try a straight-on dial photo in better light", top-3 shown without a big headline. Out-of-scope variant: "This does not look like a supported Rolex" with the three photo tips and the supported-models list. Drop the 14-row table from the main view; keep it under "Full scores" for the technical reader, rounded to whole percents.

**4. Model detail page** (one per variant, linked from results, search and nickname lookups). Own-written text; facts from primary sources.

```
+--------------------------------------------------------------+
| Models > Submariner > Submariner Date 126610LN               |
| [photo, licensed]   Rolex Submariner Date                    |
|                     Ref 126610LN | Status: current           |
|                     Also known as: (unofficial nicknames)    |
|  Specs: case 41 mm | calibre | water resistance | bezel      |
|  Timeline: 16610 (2010 gen) -> 116610 -> 126610 (2020-)      |
|  How to tell it apart: [bezel] [case size] [calibre] [ref]   |
|  Often confused with: 124060 (no date) | 126610LV (green)    |
|  Market (optional): median + range, "as of" date, source     |
|  Links: Rolex.com | listings | buying guide                  |
|  Not authentication. Prices vary widely by source.           |
+--------------------------------------------------------------+
```

Why: this answers the "I want to know more" complaint and mirrors the structure of strong guides (reference table, years, how-to-choose, FAQ). Price data is optional and risky: retail figures for one reference differed across sources ($8,100, $9,200, $10,050), so any price needs a date, a source and a range, not a single number. Skip it if you cannot source it.

**5. Model card page** (the employer page). Sections: intended use and non-use (no authentication, no valuation), data sources and licences, training split, **top-1 and top-3 at family and variant level**, macro-F1, per-class confusion matrix, accuracy by photo type (studio, wrist, low light, off-angle) with confidence intervals, out-of-scope detection results, latency p50 and p95 including cold start, known failure images, version and date. Add an architecture diagram (browser to static host to Modal) and links to repo and tests. Model cards are a documented standard for exactly this ([Mitchell et al.](https://arxiv.org/abs/1810.03993v2)), and hiring-advice sources list live demo, honest metrics, limitations and clear repo structure as what reviewers look for (Springboard, DataExpert, reported secondhand in the notes).

## Benchmark plan

Goal: replace "accuracy not high" with numbers you control, and compare fairly with the market.

**Test set.** Freeze 20 to 50 photos per reference where possible, at least 5 per family, from sources disjoint from training: your own shots, friends' wrist photos, openly licensed images. Check near-duplicates against the training set with embeddings, since the current train/val/test split may leak across the same listing (the repo does not say). Tag each photo: studio, wrist, clutter, low light, off-angle, low resolution. Include a **negative set**: other brands (Omega, Tudor), look-alikes and non-watches.

**Metrics.** Top-1 and top-3 at family and reference level; macro-accuracy and macro-F1 so Datejust cannot hide Milgauss; confusion matrix; accuracy per photo type with Wilson or bootstrap intervals; calibration error; AUROC and false-positive rate on the negative set; accuracy against coverage (what happens if the tool abstains on low confidence); p50 and p95 latency, warm and cold. Run `evaluate.py` first, since it produces the only metric that exists, then extend it (scikit-learn is already in requirements).

**Competitors.** Run the same frozen photos through Chrono24's scanner, Google Lens and one or two free web tools (Grailr, WatchScanning) by hand on a small subset, and through a general vision LLM via API with a fixed prompt ("name the Rolex model and reference, give top-3"). Manual tests are not reproducible, so record the date, app version and screenshots. Never claim to "beat Google" without matched samples. Many vendor accuracy claims (Watchpedia over 95%, Chronos 98%) are unverified marketing, so do not use them as your baseline ([Watchpedia](https://apps.apple.com/us/app/id6753745167)).

**Output.** A README table, the model card page, a failure gallery and an "evaluated on [date], [N] photos" line on the landing page. State that reference-level accuracy will be lower than family-level; reporting both is more credible than one flattering number.

## Caveats on the evidence

Treat these limits as part of the finding. No independent accuracy benchmark of any watch-ID app or LLM on watches was found, so competitor "accuracy" is vendor claim or a single 2019 hands-on test where Chrono24 handled popular watches and failed on obscure, vintage and angled photos ([WatchGecko](https://www.watchgecko.com/blogs/magazine/the-new-chrono24-watch-scanner)). That test is old, and Chrono24's current scanner was not verified. Chrono24, WatchCharts, WatchPatrol and Rolex.com returned HTTP 403 to fetches, so their features are known only from search snippets and old articles; layout details (galleries, compare tools, filters) are unverified, and no result-page screenshots were seen. Whether any competitor shows ranked alternatives was not confirmed either way. No Reddit or Play Store review content was found, and App Store ratings are tiny samples (watchID 4.0 from 8 ratings; WatchSnap 4.8 from 57, developer-replied), so no community sentiment is claimed. Chrono24's training size is reported inconsistently (1M or about 2M images). Hiring-manager advice comes from career blogs, not studies. The codebase audit was a read-only review: the layout overlap, no-watch screen and preprocessing bugs are derived from code and CSS and were not screenshot-tested, and neither `/predict` latency nor any model accuracy was measured. The cold-start breakdown is inferred. Modal's `min_containers` billing and Render's service type are unverified. The dataset, retrieval and calibration recommendations rest on general computer-vision papers, not watch studies, so each needs your own A/B test. Not legal advice on scraping or trademarks; the training data is scraped from one retailer, so keep it separate from displayed images and never redistribute it.

## Conclusion

The notes point to a reframing: Rolex Finder does not need a better model first, it needs to prove the model it has. Competitors are not visibly more accurate; they are more informative and more transparent about their data, and almost none publishes numbers. A modest, honest benchmark with a clear model card, plus honest failure states, would put a free student project ahead of paywalled clones on the one dimension employers can check in two minutes.

The build order follows from that. Ship the cheap trust fixes (states, examples, names, benchmark) before touching the model, because they cost days and change the first impression. Then fix preprocessing bugs and measure, so each change shows up as a number in the model card. Only after that is retrieval-based variant matching and brand expansion worth the effort, since both need data and a benchmark to be defensible. The result, in screens 1 to 5 above, is a tool that says what it knows, what it does not, and where to learn more.
