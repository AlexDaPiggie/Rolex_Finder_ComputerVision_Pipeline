# Rolex Finder UI patterns: status, loading, error, no-result, confidence, examples, editorial look

Method note: ~20 tool calls. Many sites blocked fetches (Rolex.com 403, Hodinkee blocked, iNaturalist help 403, Remove.bg returned no example text). The Apple HIG pages returned only titles, so the Apple bullets below are the fetch tool's paraphrase of general HIG guidance, NOT verified quotes. Items marked "Inference" are my recommendations, not sourced facts. Everything under "Gaps" could not be verified.

## 1. Cold start / long wait (10-45 s)

### Takeaway
Real products mostly show an indeterminate state plus a plain sentence near the content it replaces. Guidance says do not fake progress. For a 10-45 s wait with unknown length: one honest sentence, a thin indeterminate line, and a later second sentence if it runs long. No percent bar.

### Cited Findings
- Render free services spin down after 15 min idle; restart takes about one minute and "Render displays a loading page to connecting browsers" (exact loading-page wording not confirmed) - [Render docs](https://render.com/docs/free)
- Hugging Face free Spaces "go to sleep" after inactivity; owner or visitor restarts them (visitor-facing sleeping/building screen wording not retrieved) - [HF Spaces overview](https://huggingface.co/docs/hub/spaces-overview)
- HF lets Spaces preload models at build time to cut startup time (the fix for cold start, not a UI pattern) - [HF config reference](https://huggingface.co/docs/hub/spaces-config-reference)
- GitHub Primer loading thresholds: under 1 s show nothing; 1-3 s indeterminate; 3-10 s determinate if possible; over 10 s determinate and ideally background. Loading text can accompany any indicator; be specific ("loading status checks"). Place the indicator near the content it replaces; avoid layout shift - [Primer loading](https://primer.style/product/ui-patterns/loading/)
- Apple HIG (paraphrase via fetch tool, unverified): use indeterminate when duration unknown; "don't fake progress"; label what is happening - [Apple progress indicators](https://developer.apple.com/design/human-interface-guidelines/progress-indicators)
- Gradio: cached examples bypass the queue so progress and info toasts are not shown for them; Gradio otherwise has its own queue/progress UI - [Gradio Examples docs](https://www.gradio.app/docs/gradio/examples)
- Shazam, Google Lens, Pl@ntNet, Merlin, Vivino, Chrono24 scanner: no citable description of their waiting UI found.

### Inferences
- Primer's 10 s+ rule wants determinate progress, but a cold start is unmeasurable. Honest alternative: indeterminate line plus staged sentences tied to real events (request sent, server answered, model read). Only show a stage if the API truly reports it.
- Status lives best (a) in the primary button label (replaces "Identify" while working) and (b) one sentence under the image. No chip, no dot.

### Pattern to copy
- Show the user's own photo at once; button becomes "Identifying" (disabled).
- One-pixel gold rule under the photo with slow indeterminate sweep (ease-out, no bounce).
- Sentence 1 at 0 s: "Reading the dial and case."
- Sentence 2 only after about 8 s of no response: "The server was asleep. First look takes up to 45 seconds."
- After about 45 s: stop, show error with Retry. Never loop silently.

### Pattern to avoid
- Pill chip with glowing/pulsing dot. Critics call it "decoration cosplaying as information" and say "If nothing is actually changing state, remove the dot entirely" - [Fountain Institute](https://www.thefountaininstitute.com/blog/signs-vibe-coded-ui), [noqta](https://noqta.tn/en/blog/ai-design-slop-overused-ui-patterns-fix-2026)
- Fake percentage bars; rotating jokes; "Our AI is thinking..." copy.

### Microcopy
- "Identifying. The first request can take up to 45 seconds."
- "The server was resting. It is awake now."
- "Still working. Thank you for waiting."

### Gaps
- Actual HF/Render/Fly/Vercel visitor-facing waking screens, Shazam/Lens/Pl@ntNet/Merlin/Vivino/Chrono24 loading UI: not fetchable or not found.

## 2. Error states (network, timeout, bad file)

### Takeaway
Good error guidance: say what happened, what to do, no blame, verb-labelled action, near the failed thing. Retain the user's input.

### Cited Findings
- GitHub Primer: failure messages "explain what went wrong and what the user can do next, such as a retry button" - [Primer loading](https://primer.style/product/ui-patterns/loading/)
- Apple HIG (unverified paraphrase): name the object ("Couldn't save Report.pdf"), no blame, short title, verb buttons like "Try Again" rather than "OK" - [Apple feedback](https://developer.apple.com/design/human-interface-guidelines/feedback)
- Google Lens 2018 failure wording reported by Gizmodo: "Hmm, not seeing this clearly yet" with a link to what Lens can and cannot identify - [Gizmodo](https://gizmodo.com/heres-hoping-google-fixes-lens-next-week-because-right-1825772069). A 2026 SEO blog claims "We can't recognize this item" (low-quality source, treat as unconfirmed) - [lensespro](https://lensespro.org/why-isnt-my-google-lens-working/)
- Stripe error-handling docs page fetched had no UI wording (SDK-only). Linear, Pl@ntNet, Vivino error text: not found.
- Primer error-messages page: URL returned the homepage only; nothing citable.

### Inferences
- Network/timeout/bad file need three different sentences; each names the actual cause (file type, size, server silent) rather than one generic error.
- Inline under the photo beats a panel: the user's image stays in view, keeps the Retry next to it.

### Pattern to copy
- Plain sentence in body type, thin gold or dark-red rule at left or top (one only), then one text-link or solid button: "Try again". Secondary: "Choose another photo".
- Layout: photo stays; message replaces the status sentence in the same spot (no layout jump).

### Pattern to avoid
- Eyebrow label + big serif headline + three bullet tips. Flagged: "Hero eyebrow / pill chip", "Repeated section kicker labels", "Oversized hero headline", plus 3-item tip grids - [Impeccable slop catalog](https://924b8765.impeccable-2rv.pages.dev/slop)
- "Something went wrong"; exclamation marks; apologising twice.

### Microcopy
- Network: "No connection to the server. Check your network and try again."
- Timeout: "The server did not answer in 45 seconds. Your photo is kept. Try again."
- Bad file: "This file is not a JPEG, PNG or WebP image under 10 MB." (use the real limits)

### Gaps
- Real Stripe/Linear/GitHub/Vivino/Pl@ntNet error layouts not verified.

## 3. "No watch found" / no-result

### Takeaway
Real tools blame the photo or database, not the user, and suggest a better photo. Best practice (inference): keep the user's image visible with a concrete instruction.

### Cited Findings
- Pl@ntNet FAQ: a failed match has two causes - species rarely illustrated in the database, or photo unusable; fix is to take new photos - [Pl@ntNet FAQ](https://identify.plantnet.org/faq). Identify page requires at least one photo of leaf, flower, fruit or bark; up to 4 photos per observation - [Pl@ntNet identify](https://identify.plantnet.org/medor/identify)
- Merlin Photo ID is "deliberately tuned to be cautious", can miss an obscured bird, and shows only the suggestion it is most confident about - [eBird support](https://support.ebird.org/en/support/solutions/articles/48001271537-merlin-photo-id-in-manage-media)
- Vivino: guidance from third parties says a failed scan is often poor light, glare, skewed angle or cropped label; fallback is search by name (exact in-app text not found) - [Invintory](https://invintory.com/blog/best-practices-for-photographing-wine-labels-for-app-accuracy/)
- Google Lens wording: see section 2.
- Remove.bg no-result wording: not found.

### Inferences
- Two reasons exist and should be named separately: (a) no watch detected in the image, (b) watch seen but not recognised. They need different next steps.

### Pattern to copy
- Show the user's photo at normal size, caption below in small type. If a detector box exists, show it or note "No case found".
- One instruction tied to the fault: "Show the dial straight on, filling most of the frame."
- Action: "Choose another photo". Optional small link "View sample photos".

### Pattern to avoid
- Sad-face illustrations, "Oops!", three-bullet tip list, cards around each tip.

### Microcopy
- "No watch found in this photo."
- "A watch was found, but it is not one of the references we know."
- "Try the dial straight on, in daylight, filling most of the frame."

### Gaps
- Actual Lens/Pl@ntNet/Merlin/Vivino/Remove.bg empty-state screens not retrieved.

## 4. Confidence display

### Takeaway
iNaturalist ranks by visual similarity and does not claim a probability; it falls back to a list when it cannot recommend. Merlin shows one cautious answer. Avoid decimals and percentages that imply precision.

### Cited Findings
- iNaturalist labels each suggestion "visually similar" or "visually similar / seen nearby"; list ranked by visual similarity; when it cannot recommend firmly it shows a few visually similar options to browse - [iNat forum thread](https://forum.inaturalist.org/t/some-interesting-ai-suggestions-of-late/34847/17), [Expected Nearby help](https://help.inaturalist.org/en/support/solutions/articles/151000170371-what-does-expected-nearby-mean-)
- Merlin: single most-confident suggestion, cautious by design - [eBird support](https://support.ebird.org/en/support/solutions/articles/48001271537-merlin-photo-id-in-manage-media)
- Google Lens, Pl@ntNet score display, Vivino: not verified. iNaturalist "we're pretty sure" phrase NOT found in my searches; do not quote it.

### Inferences
- Map model probability to three words, not numbers: Strong match / Likely / Possible. Hide percentages or show as rounded bands only in a detail view.
- Alternatives: ranked list of 3 with a reference photo thumbnail each, separated by thin rules, not cards.

### Pattern to copy
- Top result: model name large (serif), reference photo beside it, one word of confidence in body text.
- Alternatives as a plain list: thumbnail, reference, one-line difference ("Date window, no cyclops").
- Low confidence: lead with "Closest matches" instead of a named winner.

### Pattern to avoid
- "97.3%" precision; green/amber/red traffic-light badges; progress-ring gauges; "AI-powered" labels.

### Microcopy
- "Strong match." / "Likely." / "Possible - compare these."
- "No clear winner. These are the closest references."
- "Confidence is an estimate from the photo alone."

### Gaps
- Pl@ntNet and Lens scoring UI, Vivino result UI not verified.

## 5. "Try an example" pickers

### Takeaway
Little citable layout data retrieved. Gradio Examples is a labelled dataset-style row below the inputs; click fills the input.

### Cited Findings
- Gradio Examples: wraps a Dataset; default label "Examples"; label customisable; paginated (10 per page default); `example_labels` replaces rendered values with custom text; click populates inputs - [Gradio docs](https://www.gradio.app/docs/gradio/examples)
- Cached examples skip the queue, so they return instantly - same source. Useful: precompute example results so an example never hits a cold server.
- Remove.bg, Teachable Machine, Roboflow, Photoroom example rows: could not verify (remove.bg fetch returned no example content).

### Inferences
- Place directly under the drop zone, same width; 4 square thumbnails with 1 px hairline, caption = reference number ("Ref. 126610LN"), label "Or try a sample".
- Precompute results for samples (Gradio cached-example logic) so it works during cold start.

### Pattern to copy
- Thin text label + four thumbnails on one line; selected one gets underline, not shadow.

### Pattern to avoid
- Big rounded gallery cards with soft shadow; hover zoom (listed as tell: "Image hover transform", [Impeccable](https://924b8765.impeccable-2rv.pages.dev/slop)).

### Microcopy
- "No photo to hand? Try a sample."
- "Sample photos. Results are prepared in advance."

### Gaps
- Real layouts of Remove.bg, Teachable Machine, Roboflow, Photoroom, HF examples row not verified.

## 6. Luxury watch editorial visual language

### Takeaway
Only partial evidence: A Collected Man text structure and tone retrieved; Rolex.com, Hodinkee, Fratello, Chrono24, Bob's blocked or not fetched. Visual styling (fonts, rules) could not be read from page text.

### Cited Findings
- A Collected Man: repeating image / title / metadata-line modules; metadata like "October 2024 - 30 min read"; short action labels "View Collection", "Learn More"; spec filters as label above plain list of options (Capacity, Material, Colour); tone "restrained and knowledgeable", few exclamations or urgency cues (fetch-tool summary; no CSS visible) - [A Collected Man](https://acollectedman.com/)
- Rolex.com and Hodinkee: fetch failed. No verified findings.

### Inferences (from general knowledge, unverified here)
- Spec lists in watch sites are typically label left, value right, hairline between rows; no boxes.
- Use one serif display weight for model name, Inter small for data; generous whitespace; hairline rules (1 px, gold at low alpha) instead of cards.

### Pattern to copy
- Spec table: two columns, label in muted small caps-free small text, value in regular; hairline between rows.
- Reference number as the headline ("Ref. 126610LN"), name beneath.
- Plain verbs in labels: "Identify", "Choose another photo", "View reference".

### Pattern to avoid
- Cards with soft shadow around each block; icon tiles; gold gradient text.

### Microcopy
- "Reference 126610LN. Submariner Date, 41 mm."
- "Case. Oystersteel. Movement. Calibre 3235." (only if data exists)
- "Compare with the closest references below."

### Gaps
- Typography, spacing and rule treatment of Rolex.com, Hodinkee, Fratello, Chrono24 reference pages, Bob's Watches not verified.

## 7. Tell-tale "AI-generated UI" patterns and opposites

### Takeaway
Consistent critiques name the exact patterns the owner dislikes. Caveat: the Impeccable catalog comes from a vendor of critique tooling; it also lists "Cream / beige palette" and "Italic serif display headline" as tells, so the cream plus serif theme needs deliberate, non-reflexive use.

### Cited Findings
- Hero eyebrow / pill chip: fix is drop it or fold into headline. Repeated section kicker labels: use structure or imagery instead - [Impeccable](https://924b8765.impeccable-2rv.pages.dev/slop)
- Nested cards: "Cards inside cards create visual noise"; fix flatten with spacing, typography, dividers. Ghost card (hairline border plus wide soft shadow): commit to one. Extreme radius 24px+ on small cards; keep around 12-16 px - same source
- Glow: "Dark mode with glowing accents" (coloured box-shadow glows); gradient text; fix use solid colours - same source
- Icon tile above heading; numbered 01/02/03 markers unless a real sequence; bounce/elastic easing (use ease-out); identical card grids; buzzword copy ("streamline", "empower"); em-dash overuse - same source
- Seven signs: neon palettes, decorative glow, emoji icons, purple gradients, cards for every block ("Most content does not need a box around it"), multicolour side tabs, meaningless status dots - [Fountain Institute](https://www.thefountaininstitute.com/blog/signs-vibe-coded-ui)
- Same tells in a 2026 blog (pill with pulsing dot, thick side-border card, over-rounded corners) - [noqta](https://noqta.tn/en/blog/ai-design-slop-overused-ui-patterns-fix-2026). Note one source says editorial registers may legitimately use some of them.

### Opposites (summary)
- Chip with dot -> plain sentence in body text, state-linked only.
- Eyebrow + headline + bullets -> one sentence plus one action.
- Rounded shadow cards -> whitespace, hairline rules, real tables.
- Generic copy -> specific cause and next step.

### Gaps
- Dates of Impeccable and Fountain pieces not confirmed as 2024-2026 beyond the noqta "2026" slug; no peer-reviewed or major-publication critique found.

## Source reliability summary
- Verified by fetch: Render docs, HF docs, Gradio docs, Primer loading, A Collected Man, Impeccable, Fountain Institute.
- Search-snippet only: Pl@ntNet FAQ, eBird Merlin, iNaturalist forum/help, Gizmodo, Chrono24 (WatchPro: scanner matches about 15,000 watches, price from 460,000+ listings - [WatchPro](https://usa.watchpro.com/?p=50467); conflicting 2026 review says marketplace first - [popularaitools](https://popularaitools.ai/blog/grailr-watch-scanner-review-2026/)).
- Unverified paraphrase: Apple HIG.
- Failed/blocked: Rolex.com, Hodinkee, iNat help article, Remove.bg examples, Stripe/Linear UI wording.
