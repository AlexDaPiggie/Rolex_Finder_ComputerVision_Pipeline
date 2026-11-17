# ML, search, preprocessing and benchmarking for a fine-grained luxury watch identifier

Note on evidence: ~14 searches, mostly snippet-level (few full-page fetches). Many findings are general-CV evidence applied to watches by inference. Direct watch-specific benchmarks were not found. Gaps flagged per section.

## 1. Preprocessing: detection/cropping, background removal, angles, TTA, quality checks

### Takeaway
No source directly shows mask crop vs box crop improves classification accuracy; run your own A/B. Practical stack: detector box crop (YOLO fine-tuned or Grounding DINO), optional SAM 2 only if A/B shows gain, plus cheap quality gates (blur, size, "is watch").

### Cited Findings
- Common pattern: Grounding DINO localises from text prompt, SAM 2.1 segments from boxes; a fine-tuned YOLOv11 can replace the detector in a supervised variant (bird segmentation paper, IoU 0.912 for YOLOv11+SAM 2.1) - [arXiv 2603.00184](https://arxiv.org/pdf/2603.00184v2). Measures segmentation quality, not classification.
- Grounding DINO beat YOLO-World on IoU/precision/recall in a blueberry annotation study, but SAM2-Large had significantly longer processing time - [PMC12694221](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12694221/)
- Zero-shot open-vocab detectors struggle at fine-grained class distinctions (so use them for "find the watch", not "which watch") - [arXiv 2504.07252](https://arxiv.org/pdf/2504.07252)
- Roboflow Universe hosts several watch detection datasets (e.g. 5163-image "Object Identifying Watch Model"); label granularity unverified - [Roboflow](https://universe.roboflow.com/syed-hussain-agb4f/object-identifying-watch-model-eftoz)
- Kaggle "Human Wrist Image Dataset" has wrist+watch images with classification/detection annotations, aimed at detection/AR not model ID - [GTS.ai](https://gts.ai/dataset-download/human-wrist-image-dataset/)
- Blur gate: variance of Laplacian on grayscale, threshold on "blurry" - fast, simple - [PyImageSearch](https://pyimagesearch.com/2015/09/07/blur-detection-with-opencv/). Threshold is dataset-dependent, needs tuning on your own sharp/blurry samples; unreliable with varied lighting - [PyImageSearch via mirror](https://m.elecfans.com/article/2150267.html)
- Competing apps (Chrono24 scanner, watchID, Grailr) advise clear well-lit dial photos and reviewers note reliance on image quality - [WatchGecko](https://www.watchgecko.com/blogs/magazine/the-new-chrono24-watch-scanner), [Grailr](https://grailr.watch/identify)

### Inferences
- Cheapest first step: crop to watch box with margin (~10-15%), resize to model input, keep some background in training (augment) so model is robust to crop errors.
- SAM 2 adds latency/GPU cost (per blueberry study); only adopt if A/B on held-out wrist/clutter images shows gain. Likely small win for dial-centric ID.
- Quality gates to implement: min short side (e.g. <224 px warn), Laplacian variance tuned on own data, detector confidence for "no watch found", plus OOD score (section 3). Show specific user feedback ("blurry", "too far", "no watch detected, try dial face-on").
- TTA: horizontal flip is NOT safe for dials/text/crown side asymmetry; prefer multi-crop/scale TTA. Evidence not found in sources (see gaps).

### Gaps
- No source comparing mask vs box crops on downstream classification accuracy.
- No cited evidence on TTA benefit for fine-grained watch ID or on angle-robustness methods; no recommended blur/min-resolution thresholds (must be calibrated).
- Chrono24 scanner internals unknown.

## 2. Model/retrieval: classifier vs embedding retrieval, hierarchy, few-shot, fine-tuning, imbalance

### Takeaway
For many references with few images each and new references added often, frozen-embedding kNN/prototypes (DINOv2/DINOv3/SigLIP 2 + flat FAISS) is cheap and extensible; keep the fine-tuned classifier for family level and compare on your own data. No head-to-head watch evidence exists; benchmark both.

### Cited Findings
- No standard DINOv3 vs SigLIP 2 comparison on fine-grained retrieval found; one practitioner guide says self-supervised encoders tend to beat text-aligned spaces on near-duplicate / fine-grained instance retrieval, and says to benchmark on own data - [Roboflow comparison](https://playground.roboflow.com/models/compare/dinov2-vs-siglip), search summary
- DINOv3 (7B, 1.7B images) claims SSL beats weakly-supervised models on probing incl. fine-grained classification - [Meta DINOv3](https://ai.meta.com/dinov3/), [arXiv 2508.10104](https://arxiv.org/abs/2508.10104). Counter-evidence: in a 37-image emerald grading study DINOv3 underperformed SigLIP 2 etc. across probes (narrow domain) - [arXiv 2605.15599](https://arxiv.org/pdf/2605.15599)
- SigLIP 2 outperforms SigLIP at all scales, mainly image-text tasks - [arXiv 2502.14786](https://arxiv.org/pdf/2502.14786v1)
- FungiTastic (fine-grained few-shot): centroid prototypes always beat nearest-neighbour on pretrained descriptors, and DINOv2/CLIP embeddings beat classifiers trained on the small in-domain set - [arXiv 2408.13632](https://arxiv.org/pdf/2408.13632)
- kNN on frozen DINOv2-L, no backprop, beats meta-learning baselines on 4 few-shot benchmarks (preprint, little detail) - [arXiv 2602.05271](https://arxiv.org/html/2602.05271v1)
- PCA whitening of DINOv3 features lifted prototype accuracy ~30% to ~55% in a fungi task (listing only) - [CVPR 2026 listing](https://en.papernotes.org/CVPR2026/segmentation/training-free_fine-grained_semantic_segmentations_in_low_data_regimes_a_fungitas/)
- Prototypes from very few new samples are biased - [arXiv 2602.05271](https://arxiv.org/html/2602.05271v1)
- FAISS: Flat (exact) for small collections, guides put the cut around 10K-100K vectors; HNSW for ~100K+; Lin 2024 asks what "rather small" means - [Zilliz](https://zilliz.com/learn/choosing-right-vector-index-for-your-project.md), [arXiv 2409.06464](https://arxiv.org/pdf/2409.06464v1.pdf). Official FAISS wiki thresholds not verified.
- Existing HF/Kaggle watch data is thin: `pk3388/test_watches` (no card), `noxneural/watches_chrono24` (gated), Kaggle "Watches of all range" is metadata only - [HF pk3388](https://huggingface.co/datasets/pk3388/test_watches), [HF noxneural](https://huggingface.co/datasets/noxneural/watches_chrono24/tree/main/Apple), [Baselight](https://baselight.app/u/kaggle/dataset/anas123siddiqui_watches_of_all_ranges)

### Inferences
- Dataset size (likely <100K vectors) means `IndexFlatIP` on L2-normalised embeddings is enough; no ANN needed. Store embeddings in .npy and load in Modal.
- Hybrid: family classifier (current) -> restrict kNN search to that family's references -> return top-3 reference IDs; hierarchical gating reduces confusions across families. Also use kNN as a second opinion: disagreement between classifier and retrieval = low-confidence signal.
- Adding a new reference = embed 5-20 photos, add prototype; no retraining. Use centroid prototype per reference, plus multi-view (dial, case side, caseback) as separate prototypes.
- Class imbalance: class-weighted loss or balanced sampling, report macro-accuracy not just overall (standard practice; no source fetched).
- Fine-tuning ConvNeXt/ViT: no watch-specific source found; treat as experiment (linear probe on frozen features first, then partial fine-tune).

### Gaps
- No direct watch-reference retrieval benchmarks or papers found.
- No evidence on multi-view fusion, imbalance handling, or ConvNeXt vs ViT for watches.
- DINOv3 license/commercial terms not checked.

## 3. Calibration and honesty: temperature scaling, top-k, OOD/open-set, low-confidence states

### Takeaway
Fit temperature on a held-out split, show top-3 not just top-1, add a separate OOD score (energy or max-logit/MCM-style) and an explicit "not sure / maybe not a Rolex" state. Calibration and OOD detection need separate evaluation.

### Cited Findings
- Energy score works post-hoc on pretrained models without retraining; cut avg FPR95 by 18.03% vs softmax confidence in a CIFAR-10 comparison - [arXiv 2010.03759](https://arxiv.org/pdf/2010.03759)
- Temperature tuned for OOD separation (ODIN, T=1000) may stop being meaningful as predictive confidence; evaluate separately - [arXiv 2110.14051](https://arxiv.org/pdf/2110.14051)
- Open-set calibration: temperature scaling on a 10% held-out validation split improved open-set ECE 0.346 -> 0.230, still far worse than closed-set (0.069 -> 0.011) - [arXiv 2205.07160](https://arxiv.org/pdf/2205.07160)
- MCM: training-free zero-shot OOD via max softmax-scaled cosine similarity to class text prototypes; official repo supports MCM, energy, max-logit with CLIP - [arXiv 2211.13445](https://arxiv.org/pdf/2211.13445.pdf), [GitHub](https://github.com/deeplearning-wisc/MCM). Reported figures (e.g. CLIP-L avg AUROC 91.49%) are from a review and partly flagged unverified.
- Conformal prediction (RAPS) gives sets guaranteed to contain true class at chosen probability; on ImageNet at alpha=10% APS ~19 labels vs RAPS ~2. Guarantee is marginal, not per-class/per-image - [arXiv 2009.14193](https://pdf.arxiv.org/pdf/2009.14193), [MAPIE](https://mapie.readthedocs.io/en/latest/theory/classification/)
- Human study: RAPS sets helped labeling on hard OOD images but sets grew large; top-k did better on easy OOD - [arXiv 2401.08876](https://arxiv.org/pdf/2401.08876)

### Inferences
- Recommended UI states: High (top-1 prob above threshold and kNN agrees) / Medium (show top-3) / Low (show "not sure" + retake tips) / Out-of-scope ("doesn't look like a supported Rolex"). Thresholds chosen on a validation set including non-Rolex and other-brand watches as negatives.
- Include other-brand watches (Omega, Tudor, fakes-lookalikes) and non-watch images as an explicit "other" test set to measure AUROC/FPR95 of the OOD score; add them to training as a reject class if score alone is weak.
- Fakes: visual classifiers cannot authenticate; state this explicitly in the model card (no source needed, scope statement).
- Conformal sets via MAPIE are cheap and give a defensible "95% sets" claim, but guarantee holds only on same distribution as calibration data (user photos differ from catalog images).

### Gaps
- No fine-grained-specific open-set results found.
- No watch-specific calibration numbers.

## 4. Brand expansion (Omega, Patek, AP, Seiko, Cartier): datasets, scraping legality, scale

### Takeaway
Public labelled watch data is scarce and low-quality; real expansion means collecting own data. Scraping legality is jurisdiction-dependent and unsettled; prefer licensed/own-photographed/user-contributed data and respect opt-outs.

### Cited Findings
- Public options found: HF `pk3388/test_watches` (AP, Tissot, Vacheron etc., no card), gated `noxneural/watches_chrono24`, Roboflow detection sets, `watch-watcher` project trained on Chrono24 scrape with ResNet50 - [GitHub](https://github.com/kevintang513/watch-watcher). Licences/label quality unverified.
- US: Ninth Circuit (hiQ v. LinkedIn, 2019) held CFAA did not bar scraping public pages; circumventing access controls may still be problematic - [Zyte summary / search results](https://www.zyte.com/blog/ai-web-scraping-legal-risks/)
- EU: TDM exception (Art. 4, Directive 2019/790) allows mining unless rights expressly reserved in machine-readable form; AI Act providers need policies to respect reservations - [Brodies](https://brodies.com/insights/ip-technology-and-data/ais-data-goldmine-navigating-data-scraping-by-ai-products/), [GT Law](https://www.gtlaw.com/ar/insights/2024/7/eu-ai-acts-opt-out-trend-may-limit-data-use-for-training-ai-models)
- Kneschke v. LAION (Hamburg 2024): claim dismissed, TDM exception applied; machine-readability of opt-out contested, first-instance only - [MoFo](https://www.mofo.com/resources/insights/241004-to-scrape-or-not-to-scrape-first-court-decision)

### Inferences
- Not legal advice. Safer sources: own photos, user submissions with consent, manufacturer/press images only with permission, Wikimedia Commons CC images, brand-licensed catalogues. Scraped marketplace photos carry ToS and copyright risk; training use is more defensible than redistribution, so never redistribute the dataset.
- Scale heuristic from FungiTastic evidence: with frozen embeddings, 5-20 clean images/reference gives usable prototypes; a classifier head needs more. (Heuristic, not a measured watch number.)
- Add brands in family-tier order: brand classifier first (cheap, many images), then per-brand family retrieval.

### Gaps
- No verified dataset size/quality for Omega/Patek/AP/Seiko/Cartier; no 2026 legal updates confirmed (EU AI Act code of practice, US fair-use rulings not found in these searches).
- Marketplace ToS (Chrono24, eBay) not read.

## 5. Benchmarking: fair protocol, competitor comparison, model card

### Takeaway
Build a source-disjoint test set (photos the model never saw, from different photographers/platforms/angles), report top-1/top-3, macro-accuracy, per-class confusion, OOD metrics and latency, and publish a model card. Compare vs Chrono24 scanner and general MLLMs on the same frozen set with a fixed prompt.

### Cited Findings
- Model cards (Mitchell et al.) = short docs reporting intended use, evaluation data, per-subgroup performance, limitations - [arXiv 1810.03993](https://arxiv.org/abs/1810.03993v2)
- Chrono24 offers a wrist-photo scanner returning reference, material and value (single hands-on test only) - [WatchGecko](https://www.watchgecko.com/blogs/magazine/the-new-chrono24-watch-scanner)
- Many AI watch apps (watchID, Grailr, Patina, Watchpedia) exist; accuracy claims (e.g. Watchpedia >95%) are vendor claims, unverified - [Watchpedia](https://apps.apple.com/us/app/id6753745167)
- MLLMs vs specialists: GPT-4o-class models lag specialist vision models on classification tasks (ICLR 2026 paper) - [arXiv 2507.01955](https://arxiv.org/pdf/2507.01955), [ICLR](https://proceedings.iclr.cc/paper_files/paper/2026/hash/dcaa785639b161965b23f93abb4d9397-Abstract-Conference.html). Fine-grained categories are a weakness: models do well at superordinate level but fail at finer categories (FINER) - [arXiv 2402.16315](https://arxiv.org/html/2402.16315v4)
- Standard pitfall: calibration set and test set must be separate; open-set ECE is much worse than closed-set (above, arXiv 2205.07160).

### Inferences (protocol)
1. Freeze test set (e.g. 20-50 photos x reference or at least 5 per family) from sources disjoint from training (different sellers/photographers; dedupe via embedding near-duplicate check against training set to avoid leakage).
2. Strata: catalog/studio, wrist, clutter, low light, off-angle, low-res; report accuracy per stratum with confidence intervals (Wilson/bootstrap).
3. Metrics: top-1/top-3 at family and reference level, macro-F1, per-class confusion matrix, ECE, AUROC/FPR95 on non-Rolex negatives, coverage vs accuracy curve (selective prediction), p50/p95 latency incl. cold start on Modal.
4. Competitors: run Gemini/GPT/Claude vision with a fixed prompt ("name the Rolex model/reference, give top-3") via API, human-score or exact-match against ground truth; Google Lens and Chrono24 scanner manually on a small subset (no API, note manual and possibly non-reproducible).
5. Publish: README table + model card with data sources, limits (no authentication/fakes, lighting), version, date, test-set size and CIs. Avoid overclaiming "beats Google" without matched samples.

### Gaps
- No independent published benchmark of watch-ID apps or MLLMs on watches found; no head-to-head GPT-4o/Gemini/Claude numbers on fine-grained sets found.
- Google Lens watch behaviour unverified.

## 6. Multimodal LLM as fallback/explainer vs custom model; cost/latency

### Takeaway
Use the custom model as primary (specialists beat MLLMs at fine-grained classification); call an MLLM only for low-confidence cases or for natural-language explanation, constrained to the model's top-3 candidates.

### Cited Findings
- MLLMs lag specialists on classification and struggle with fine categories (sources in section 5).
- Zero-shot classification via MLLM-generated descriptions plus a classifier improved avg +6.2 points across 10 benchmarks vs prior methods - [arXiv 2405.15668](https://arxiv.org/pdf/2405.15668)

### Inferences
- Fallback design: only on Low-confidence state, pass image + top-3 candidates (with reference image snippets) and ask the MLLM to pick/abstain and explain visible features (bezel, dial, crown guard). Constrains hallucination, cuts cost since only a fraction of requests hit the API.
- Cost/latency: current prices not retrieved here (check provider pricing pages; they change); expect 1-5 s vs tens of ms for local embedding. Add rate limit and caching by image hash.
- Explainer risk: the LLM can fabricate reasons; label as "AI description, not verification".

### Gaps
- No 2026 pricing/latency figures fetched; no evidence on MLLM re-ranking accuracy gains for watches.

## 7. Search: what it could mean and cheap implementations

### Takeaway
Three cheap features: (a) visual similar-watch search from the same embeddings + flat FAISS, (b) text search over a reference/nickname table, (c) filters (family, size, material, era). All run without a vector DB at this scale.

### Cited Findings
- Flat exact search is the default for small collections; HNSW only from ~100K vectors - [Zilliz](https://zilliz.com/learn/choosing-right-vector-index-for-your-project.md), [arXiv 2409.06464](https://arxiv.org/pdf/2409.06464v1.pdf)
- CLIP/SigLIP-style models allow text-to-image queries (zero-shot prompts without training data) - [Soup-Adapters, arXiv 2507.05807](https://arxiv.org/pdf/2507.05807)
- Reference-number-returning scanners are the competitor norm (Chrono24, Grailr) - [WatchGecko](https://www.watchgecko.com/blogs/magazine/the-new-chrono24-watch-scanner)

### Inferences
- Visual: reuse the identification embedding; "similar watches" = top-k neighbours across references, deduped per reference. Free once embeddings exist.
- Text: JSON/SQLite table of reference, nickname (Submariner "Kermit", "Hulk", "Pepsi"), family, dimensions; client-side fuzzy search (Fuse.js) or SQLite FTS5. Optional SigLIP text-to-image query for descriptive searches ("green dial with date"), but expect weaker fine-grained accuracy; test first.
- Filters: metadata facets over the same table; combine with kNN by pre-filtering vectors (cheap with flat search).
- Scope fit: marketplace/price search needs external data and licensing; out of cheap scope.

### Gaps
- No source on user demand for each search type; no UX evidence (covered by other researchers).
