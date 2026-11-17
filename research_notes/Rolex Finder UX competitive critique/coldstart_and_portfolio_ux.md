# Cold-start handling and ML/CV portfolio demo UX (as of Nov 2026)

Note: ~15 tool calls. Several claims rest on search-engine summaries of third-party pages, flagged below. Primary sources fetched directly: Modal pricing, Modal cold-start guide, Render free docs, NN/g response times, web.dev capture.

## 1. Cold-start UX patterns (progress, pre-warm, examples, errors)

### Takeaway
A 40-50 s wait is far past Nielsen's 10 s attention limit, so it needs a determinate-style, honest, staged progress UI, a silent pre-warm ping on page load, and instant pre-cached sample results so the first impression never depends on the cold start.

### Cited Findings
- 0.1 s feels instant; 1 s keeps flow of thought; 10 s is the limit for keeping attention. Beyond that users switch tasks and need feedback on when the system will finish. Percent-done indicators for operations over ~10 s — [NN/g](https://www.nngroup.com/articles/response-times-3-important-limits/)
- Progress indicators reassure the system has not crashed, show roughly how long to wait, give something to look at — [NN/g](https://www.nngroup.com/articles/response-times-3-important-limits/)
- Nielsen's guidance: progress bar must never stall, lie, or reset; an approximate ETA is fine (secondary summary) — [UX Tigers](https://www.uxtigers.com/post/progress-indicators)
- Skeleton screens: sources disagree. One controlled test (Viget, "A Bone to Pick with Skeleton Screens") found skeletons gave the longest perceived wait of three treatments; skeletons suit short waits, determinate bars suit long ones (secondary summary) — [UX Planet](https://uxplanet.org/progress-indicators-4-common-styles-91a12b86060c), [UX Tigers](https://www.uxtigers.com/post/progress-indicators)
- Google 2016: 53% of mobile visits abandoned if page takes >3 s; data is from 2016 3G/4G conditions and is about page load, not tool inference — [Think with Google](https://thinkwithgoogle.com/_qs/documents/57/mobile-page-speed-new-industry-benchmarks.pdf), [Marketing Dive](https://www.marketingdive.com/news/google-53-of-mobile-users-abandon-sites-that-take-over-3-seconds-to-load/426070/)
- Modal docs name two cold-start causes: queueing while a container boots, and first-call initialisation like loading weights — [Modal cold-start guide](https://modal.com/docs/guide/cold-start)

### Inferences
- Recommended UI (my synthesis, not sourced): on page open, fire a silent `GET /health` (or tiny warm-up call) to Modal and to the Render backend; show a small "Engine warming up (~30-45 s first visit)" chip that flips to "Ready"; disable nothing, queue the upload.
- On submit during cold: staged messages tied to real phases ("Waking server", "Loading model", "Analysing image") with an honest "first request can take up to a minute" note, elapsed-time counter, and a determinate-ish bar that eases to ~90% and never resets. Use a client timeout (~90-120 s) with a retry button and a plain-English error, not a blank spinner.
- "Try these examples" thumbnails with precomputed JSON results (static, shipped with frontend) return in under 0.1 s and let a recruiter see the full result page even if the backend is cold. Label them clearly as precomputed samples; offer "run live" as an option.
- Optimistic UI: show image preview and the result-page layout (skeleton for the card) immediately after selection; skeleton is fine here as the wait ends once warm.

### Gaps
- No primary NN/g article on skeleton screens retrieved. No sourced data on abandonment specific to 30-60 s inference waits.

## 2. Technical mitigations (Modal, Render, hosting alternatives, pings)

### Takeaway
Cheapest real fix: put the frontend on static hosting (no spin-down), keep the model on Modal with a CPU-sized/ONNX model and, if affordable, `min_containers=1` (about $29/month for 0.5 core + 2 GiB, which nearly equals the free $30 credit; GPU warm is ~$430/month, not viable). Otherwise use memory snapshots plus a pre-warm ping.

### Cited Findings
- Modal Starter: $0 base, "$30 / month free credits" covering GPU, CPU, memory. Rates: CPU $0.0000131 per core-second (min 0.125 core), memory $0.00000222 per GiB-second, T4 $0.000164/s, L4 $0.000222/s — [Modal pricing](https://modal.com/pricing)
- `scaledown_window`: default 60 s, range 2 s to 20 min; you pay while idle. `min_containers` puts a floor on containers so the function does not scale to zero; idle containers cost money. `buffer_containers` for bursts. Memory snapshots capture memory after warm-up and reuse it. Also bake weights into the Image/Volume, load in `@modal.enter` — [Modal cold-start guide](https://modal.com/docs/guide/cold-start)
- Raising scaledown_window alone does not help a function that scales from zero (secondary summary of same guide) — [Modal cold-start guide](https://frontend.modal.com/docs/guide/cold-start)
- Memory snapshots: only for deployed apps; GPU snapshots are alpha/experimental (`enable_memory_snapshot=True`, `experimental_options={"enable_gpu_snapshot": True}`, init in `@modal.enter(snap=True)`); will not help much if most startup is loading weights; incompatible with multi-GPU; torch compile can break snapshot creation — [Modal memory snapshots](https://modal.com/docs/guide/memory-snapshots), [GPU snapshot example](https://modal.com/docs/examples/gpu_snapshot)
- Modal-reported speedups: Parakeet ~20 s to ~2 s (July 2025); Ministral 3 3B median cold start ~118 s to ~12 s (Dec 2025) — [Modal blog GPU snapshots](https://modal.com/blog/gpu-mem-snapshots), [Modal blog Mistral 3](https://modal.com/blog/mistral-3)
- Render free web service spins down after 15 min without inbound traffic; spin-up "takes about one minute"; 750 free instance hours per workspace per month, then suspended; `/robots.txt` requests do not wake the service. Docs do not address keep-alive pings — [Render docs](https://render.com/docs/free)
- Render timeout was reduced 30 to 15 min in Sept 2025 (third-party; older articles say 30) — [temps.sh](https://temps.sh/blog/render-pricing-2026)
- Render paid instance from ~$7/month removes spin-down (third-party) — [livemy.app](https://livemy.app/blog/render-pricing)
- Cloudflare Pages Free: unlimited static requests and bandwidth, 500 builds/month, 100 custom domains (per search summary of Cloudflare pricing) — [Cloudflare Pages](https://pages.cloudflare.com/)
- Vercel Hobby is restricted to personal, non-commercial use; ~100 GB bandwidth (third-party) — [Vercel Hobby docs](https://vercel.com/docs/plans/hobby-plan)
- Hugging Face Spaces: free cpu-basic sleeps after 48 h inactivity, any visitor wakes it. Forum reports (unconfirmed, user posts) of free CPU Basic access tightening in 2026 and ZeroGPU free quota ~5 GPU-min/day — [HF docs](https://huggingface.co/docs/hub/en/spaces-overview), [HF forum](https://discuss.huggingface.co/t/new-free-accounts-cannot-create-cpu-basic-gradio-spaces-only-zerogpu-available/177629)
- GitHub Actions: scheduled workflows in public repos auto-disable after 60 days of repo inactivity; may be delayed under load (delay claim from third party) — [GitHub docs](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows), [cronuru](https://cronuru.com/guides/github-actions-scheduled-workflows)

### Inferences
- Warm-cost arithmetic (mine, from Modal rates above, 730 h = 2.628M s): 0.5 core + 2 GiB ≈ $28.9/month; 1 core + 2 GiB ≈ $46/month; T4 ≈ $431/month. So warm-24/7 only works on small CPU model; GPU 24/7 does not fit free credit. Note credits cover only compute; verify min_containers is billed at the same rate.
- Better than 24/7: set `scaledown_window` ~5-10 min plus front-end pre-warm ping on page open; cost only when visited. Or schedule `min_containers` via Modal's API only in job-hunt windows.
- Moving frontend to Cloudflare Pages (or Netlify/GitHub Pages) removes the Render ~50-60 s layer entirely; if a Render API proxy is needed, replace with a Modal web endpoint called directly from the browser (CORS) or a Cloudflare Worker.
- Ping ethics/cost: pinging your own service every 14 min is common practice but uses Render's 750 h pool (one service 24/7 = 720 h, fits only for one service) and GitHub cron may be delayed or disabled after 60 days. Prefer pre-warm on page-open (traffic-driven, zero idle cost) and avoid hammering. UptimeRobot-style pings of Modal would bill continuous warm time.
- Model side (not sourced): if the model is small (e.g. ResNet/EfficientNet/CLIP-like), ONNX Runtime or int8 quantisation on CPU often makes GPU unnecessary and shrinks image + load time, which cuts cold start.

### Gaps
- Modal `min_containers` billing details and default not stated on the fetched page; check Modal docs. Not verified: Modal CPU cold-start times for ONNX, the actual model size in this repo, and current Netlify limits. HF free-tier changes are unconfirmed forum claims.

## 3. Hiring-manager expectations for ML/CV portfolio demos

### Takeaway
Reviewers want original, deployed, well-documented projects with live demo + repo + write-up, honest metrics and limitations, and production signals (tests, structure, reproducibility). Sources are mostly career blogs, not studies.

### Cited Findings
- Deployed model on original (non-tutorial) data; Titanic/MNIST signal tutorial completion — [Upskillist](https://www.upskillist.com/blog/10-ai-portfolio-examples-impress-recruiters/) and [DataExpert guide, Mar 2026](https://www.dataexpert.io/blog/ultimate-guide-ai-engineering-portfolios) (per search summary)
- Reviewers go to repo/live app first; 3-4 well-documented projects beat ten shallow ones; "80% more engagement" figure unverified single-blog — [MentorCruise](https://mentorcruise.com/blog/career-roadmap-how-to-build-an-ai-portfolio-that-gets-you-hired/)
- Multiple metrics (precision, recall, F1, confusion matrix), cross-validation, honest limitations — [Springboard](https://www.springboard.com/blog/data-science/machine-learning-portfolio/)
- Code review order: structure (data/models/api/tests dirs), then README — [DataExpert](https://www.dataexpert.io/blog/ultimate-guide-ai-engineering-portfolios)
- Interactive demo via Streamlit/Gradio/Flask recommended — [Dataquest](https://support.dataquest.io/en/articles/649-what-employers-look-for-in-a-portfolio)

### Inferences
- Checklist for the Rolex Finder: problem framing and dataset provenance, model card (data, intended use, limits e.g. fakes/unseen references), top-1/top-5 and per-class metrics, confusion/error analysis with failure images, architecture diagram (browser to static host to Modal), latency and cold-start numbers stated honestly, tests and CI, reproducible training (pinned env, seeds), "how it was built" write-up, live demo + repo links in header.

### Gaps
- No direct hiring-manager interviews found; no sourced examples of Teachable Machine, Google Lens, Plant.id, Vivino polish (not researched in depth).

## 4. Result-page patterns from reference apps

### Takeaway
Pattern: ranked short list with scores, each candidate illustrated by the most similar reference image, plus context (location/date) and user feedback. Limited verified detail for Merlin/Plant.id/Vivino.

### Cited Findings
- Pl@ntNet API returns top-list of species in decreasing confidence, scores 0-1; accepts up to 5 photos of one plant tagged by organ; each suggested species illustrated by the most similar dataset image — [Pl@ntNet API docs](https://my.plantnet.org/doc/api/identify)
- Pl@ntNet web app has votes on image quality, organ labels, "no plant"; model updated ~every two months with non-regression principle — [Pl@ntNet release notes](https://identify.plantnet.org/release_notes)
- Merlin Photo ID shows a short ranked list of top choices; date/location improve list and unlikely birds are flagged (the flagging claim is from a low-quality page) — [Cornell/eBird](https://ebird.org/news/merlinid), [Merlin app store page](https://apps.apple.com/app/773457673)
- Merlin original tool: correct species in top 3 about 90% of the time under test conditions — [eBird news](https://ebird.org/news/merlinid)

### Inferences
- For the watch finder: top match card (large image, brand/model/ref), calibrated confidence bar (avoid fake precision), 2-4 "similar looking" alternatives with reference photos, "not right? tell us" thumbs feedback storing image+label, low-confidence warning state ("not sure - try another angle"), "learn more" link, and "why this match" reference side-by-side.

### Gaps
- Plant.id, Vivino, Google Lens, Teachable Machine result UIs not verified. Confidence-bar specifics for Merlin not found.

## 5. Upload-tool UX and accessibility basics

### Takeaway
Use `<input type="file" accept="image/*">` with a separate "Take photo" control using `capture`, plus drag-drop, paste, preview, validation, history, shareable links.

### Cited Findings
- `capture` works on Android and iOS, ignored on desktop; values `user` (front) / `environment` (rear); on Android it launches the camera app directly and the user can no longer pick an existing picture; without `capture` mobile browsers offer camera or files — [web.dev](https://web.dev/articles/media-capturing-images)

### Inferences
- Offer two buttons ("Take photo" with `capture="environment"`, "Choose from library" without) so users are not locked to camera. Add drag-drop and Ctrl+V paste on desktop; client-side checks on type, size (resize/compress large phone photos before upload to cut upload time), preview with crop/rotate before submit; keep history in localStorage (wrapped in try/catch); shareable result links need server-side stored results with an ID (privacy: let users delete); respect `prefers-color-scheme`; keyboard-focusable dropzone, `aria-live` region for status/progress text, alt text on results. (Unsourced best practice.)

### Gaps
- Did not retrieve web.dev/MDN sources for drag-drop, paste, or WCAG status messages; image-crop UX not researched.
