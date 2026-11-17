# Rolex model detail page and marketplace/catalogue content and UX bar (as of Nov 2026)

Method note: WebSearch returns summaries; WebFetch was blocked (HTTP 403) for watchcharts.com, rolex.com, watchbase.com/terms. Chrono24, Hodinkee, Fratello, Wrist Enthusiast, Reddit pages were not directly read. Layout claims for those sites are therefore gaps, not findings.

## 1. What is on a Rolex reference/model page (content bar)

### Takeaway
The best content-led reference pages (Bob's Watches Pepsi guide, Sotheby's key-references article) combine: a per-reference table (ref, years, case, material, calibre, bezel/dial, bracelet), nickname explanation, history, price median + range + 12-month trend per reference, buyer-type advice, FAQ, and links to related/compare pages. Price-tracking sites (WatchCharts, Chrono24) add retail vs market price with dates. Fake-spotting is usually a separate guide, not on the model page.

### Cited Findings
- Bob's Watches Pepsi guide structure: key-takeaways box; "what is it" with nickname origin; table of every reference with production years and defining trait (7 refs, 6542 to 126719BLRO); history; price tables (median sold + 10th-90th percentile range) and a 12-month trend/"collectibility tier" table; "which should you buy" by buyer type; comparison with rest of family (Pepsi vs Batman premium ~25%); FAQ (7-8 entries); data-source footer (sales window and "as of" date); author byline and "reviewed by". - [Bob's Watches](https://www.bobswatches.com/rolex-blog/buying-guides/rolex-gmt-pepsi.html)
- Spec fields shown there: reference, years, material (Bakelite/aluminium/Cerachrom/904L Oystersteel), case size (38mm on 6542, 40mm from 1959), crown guards, sapphire (from 1988), water resistance, calibre (3185/3186/3285), power reserve (48h vs 70h), bracelet (Jubilee/Oyster), dial/lume. Same source.
- Bob's has no dedicated fake-spotting section on that page; it only uses calibre/power reserve to identify the steel generation when papers are missing. Same source.
- Example median sold prices on that page (Aug 2025-Jul 2026 window): 126710BLRO $24,595 (range $20,995-26,595), 16710 $15,295, 1675 $17,280. Same source. Shows the bar: price shown as median plus percentile range with sales window and date.
- Sotheby's key-references table: Ref, Years, Case, Caliber, Bezel, Dial, plus a recent auction result per ref (e.g., 6542 sold Nov 2023, 38,100 CHF); includes FAQ and nicknames list (Batman 116710BLNR, Batgirl 126710BLNR, Root Beer 126711CHNR/126715CHNR, Zombie 126713GRNR). - [Sotheby's](https://www.sothebys.com/en/articles/the-rolex-gmt-pepsi-the-key-references)
- Steel GMT-Master II "Pepsi" 126710BLRO reported discontinued April 1, 2026 (Sotheby's and Bob's both). Pepsi/Rolex never uses the nickname itself. - [Bob's Watches](https://www.bobswatches.com/rolex-blog/buying-guides/rolex-gmt-pepsi.html), [Sotheby's](https://www.sothebys.com/en/articles/the-rolex-gmt-pepsi-the-key-references). Implication: pages need a "discontinued / date" status field.
- WatchCharts model page for Submariner 124060 shows retail price (with "as of" month), market price (dated), estimated private-sale price and pre-owned dealer price, plus linked live marketplace listings. Data per search summary of: [WatchCharts](https://watchcharts.com/watch_model/21813-rolex-submariner-124060/overview) (page itself returned 403; figures: retail $10,050 Sep 2026, market $12,231 Oct 26 2026, as reported by search summary).
- Chrono24 has per-model price history ("Watch Collection", 2009 onward per a 2018 source) and a Rolex Price Index / ChronoPulse. - [Europa Star](https://www.europastar.com/1004090276.html), [The Hour Markers](https://www.thehourmarkers.com/articles/rolex-report-2026-chrono24)
- Watch Time compared Chrono24 asking vs Rolex list: 124060 lowest ask $12,995 (+60%) vs list $8,100 (older article). - [WatchTime](https://www.watchtime.com/brands/rolex-explorer-1/list-vs-ask-comparing-steel-rolex-prices-at-retail-to-prices-on-the-secondary-market)
- Retail price figures conflict across sources for 124060 ($8,100 / $9,200 / $10,050 / $16,850 AUD-unclear). - [WatchTime](https://www.watchtime.com/brands/rolex-explorer-1/list-vs-ask-comparing-steel-rolex-prices-at-retail-to-prices-on-the-secondary-market), [LuxuryBazaar](https://www.luxurybazaar.com/grey-market/?p=312), [Esquire AU](https://esquire.com.au/rolex-submariner-retail-price/)
- WatchBase: database of ~40,900 watches and 3,481 calibres; spec fields for case, dial, movement, dimensions, production years; Rolex retail prices updated Feb 2026. - [WatchBase](https://watchbase.com), [WatchBase blog](https://watchbase.com/blog/2026/02/06/rolex-pricing-updated-for-2026-on-watchbase)
- Teddy Baldassarre site (shop page fetched): filters by brand/style/price, quiz "Find the Right Watch for You", articles/videos/e-books. - [Teddy Baldassarre](https://teddybaldassarre.com/blogs/watches/fake-rolex) (fetched page was shop chrome, not the guide)
- Nickname guides are a standard content type, listing nickname, ref, colours: Hulk 116610LV, Starbucks 126610LV (some use Kermit 2.0), Kermit 16610LV, Smurf 116619LB. - [Sotheby's nicknames](https://sothebys.com/en/articles/from-pandas-to-pepsis-a-guide-to-rolex-nicknames), [Rob Report AU](https://robbreport.com.au/watches/rolex-nicknames-to-know/), [Watchmydiamonds](https://watchmydiamonds.com/?p=107527)
- Nickname conflict: "Cookie Monster" tied to ref 126619LB by one list, and to GMT 326719BLNR by another search summary; treat as unreliable. - [Rob Report AU](https://robbreport.com.au/watches/rolex-nicknames-to-know/); contradicted by [Man of Many](https://manofmany.com/watches/rolex-discontinued-watches-2026-pepsi)

### Inferences
- A result page that meets the bar needs: display name + ref + nickname(s), status (current/discontinued + date), years, a spec table, variants/related refs, price median+range with date and source, and a "how to tell similar refs apart" block.
- Price numbers must carry "as of" dates and source; sources disagree widely, so show ranges, not single points.
- Nicknames are community-defined and inconsistent; show as "also known as" and mark as unofficial.

### Gaps
- Chrono24, Hodinkee, Fratello, Wrist Enthusiast, Rolex.com model pages not read directly (403s / not reached). Layout patterns (hero + spec table, variant selector, galleries, compare tools, filters, breadcrumbs) are NOT verified from these sites. Only WatchCharts/Bob's/Sotheby's/Teddy B. structure above is evidenced, and WatchCharts only via search summary.
- "John Mayer Daytona" ref: no source found in this research (search did not confirm). From general knowledge it is Daytona 116508 green dial, unverified here.
- "Sprite" nickname unconfirmed.

## 2. Rolex families and reference naming conventions; confusions

### Takeaway
References are structured: digit-count = era, leading digits = family, last digit = metal, second-last = bezel (dress watches; unreliable for sports), letter suffix = bezel colour/gems, hyphen suffix = dial. Families are consistent enough to decode, but suffix exceptions and generation changes (1xxxxx to 2xxxxx) mean a tool should output reference-level, not just family-level, answers.

### Cited Findings
- Era: 4-digit ~1933-1988, 5-digit from 1978, 6-digit phased in 2000-2012, usually a "1" prefixed to 5-digit style; 2nd-gen 6-digit starts 12*, 22*, 33* from 2015; second digit increases when movement generation changes. - [LuxuryBazaar](https://www.luxurybazaar.com/grey-market/rolex-reference-numbers/)
- Last digit = metal: 0 steel, 1 Everose Rolesor, 2 Rolesium, 3 Yellow Rolesor, 4 White Rolesor, 5 rose gold, 6 platinum, 7 RLX titanium (2022+), 8 yellow gold, 9 white gold. Second-last digit = bezel (0 smooth/dive, 1 engine-turned/fluted, 3 fluted/diamond, 6 rotating, etc.). Same source.
- Suffix letters: LN black insert, BLNR Batman, BLRO Pepsi, SA sapphires; A/G often diamond dial; GV green sapphire on Milgauss; hyphen four digits = dial code, not part of core ref. Same source.
- Caveat: bezel digit rule applies to dress models (Datejust/Day-Date), not sports models; sources disagree on digit meaning and some old refs (6263, 1680) don't fit. - [Paul Fraser](https://www.paulfrasercollectibles.com/blogs/antiques/read-your-rolex-what-a-rolex-reference-number-means) via search summary, [Bob's 4/5/6-digit](https://www.bobswatches.com/rolex-blog/watch-101/tell-difference-4-5-6-digit-rolex-reference-number.html)
- Ref location: between lugs at 12 on older models, on rehaut on modern. Same search summary above.
- Current family count is disputed (14 vs 16 collections). Classic: Oyster Perpetual, Datejust, Day-Date, Sky-Dweller, 1908, Land-Dweller; Air-King currently only 126900 (replaced 116900 in 2022). - [Watchology](https://thewatchology.com/brands/rolex/), [Time4Diamonds](https://time4diamonds.com/blogs/articles/rolex-models-explained), [Time4Diamonds catalogue 2025](https://time4diamonds.com/blogs/articles/rolex-catalogue-2025)
- W&W 2026 (Rolex Oyster centenary): Daytona 126502 40mm Rolesium with white grand feu enamel dial and grey bezel (cal. 4131); Oyster Perpetual 28/34 in gold; OP 41 ref 134303; Yacht-Master II returned; new Day-Date 40s. - [WatchTime](https://www.watchtime.com/brands/rolex/rolex-cosmograph-daytona-126502-rolesium-enamel-grey-bezel-watches-and-wonders-2026), [Monochrome](https://monochrome-watches.com/all-the-new-rolex-models-of-2026-live-from-watches-wonders/), [Time4Diamonds 2026](https://time4diamonds.com/blogs/articles/rolex-new-releases-2026)
- 2026 discontinuations include Pepsi GMT-Master II (126710BLRO and 126719BLRO) and Datejust dial changes. - [Luxury Bazaar](https://www.luxurybazaar.com/grey-market/discontinued-rolex-2026/), [Gear Patrol](https://www.gearpatrol.com/watches/rolex-tudor-discontinued-watches-2026/)
- Within-family confusion examples evidenced: Pepsi vs Batman vs Root Beer (GMT-Master II) differ by bezel colour/suffix; steel generations 126710BLRO vs 16710 vs 116719BLRO identifiable by calibre/bracelet/ceramic; Hulk 116610LV vs Starbucks 126610LV vs Kermit 16610LV (green Submariners, differing case/gen). - [Bob's](https://www.bobswatches.com/rolex-blog/buying-guides/rolex-gmt-pepsi.html), [Sotheby's](https://www.sothebys.com/en/articles/the-rolex-gmt-pepsi-the-key-references), [Watchmydiamonds](https://watchmydiamonds.com/?p=107527)

### Inferences
- Model-ID output should be ref-level with confidence and top-k alternatives, since many refs differ only by bezel colour, bracelet or generation (hard visually). Pairs likely to confuse a classifier: 124060 vs 126610LN vs 126610LV (Sub no-date/date/green); GMT-Master II colourways; Datejust 36/41 vs Oyster Perpetual (differ by date window/dial); Explorer vs Explorer II vs Air-King; Daytona metals/dials.
- Display names should follow Rolex's own: Oyster Perpetual, Datejust, Day-Date, GMT-Master II, Sea-Dweller, Deepsea, Sky-Dweller, Yacht-Master, Cosmograph Daytona, Air-King, Explorer, Land-Dweller, 1908. Add a "legacy/discontinued" flag for Milgauss, Cellini, Turn-O-Graph, etc. (statuses unverified, see Gaps).
- Reference digit decoder (as in LuxuryBazaar's lookup tool) is a cheap, high-value feature and a sanity check on model output.

### Gaps
- Status of Milgauss, Cellini, Turn-O-Graph, Thunderbird, Explorer II 226570, Sea-Dweller, Deepsea not confirmed by searches. Need Rolex.com catalogue (403).
- Rolex.com official names list not obtained.
- 116508 vs 126508 vs 126518 vs 126503 differences not confirmed in results.

## 3. How enthusiasts would use an ID tool; realistic vs risky use-cases

### Takeaway
Identification (what model/ref is this?) is realistic; authentication is not. Practitioner sources say photo-only authentication is unreliable and in-person inspection (caseback/movement) is definitive. A tool should say "looks like X" with confidence, and explicitly refuse to say real or fake.

### Cited Findings
- r/rolex runs a "Watch Verification Thread" asking for specific photos and noting phone cameras that distort text make photos unusable for verification (2022 thread). - [r/rolex mirror](https://lr.us.psf.lt/r/rolex/comments/vquk5u/watch_verification_thread_if_youre_uncertain_if_a)
- Authentication guides stress multiple independent checks, in-person beats photo, and caseback/movement is definitive. - [SwissWatchExpo](https://www.swisswatchexpo.com/thewatchclub/how-to-spot-a-fake-rolex/), [Everest Bands](https://everestbands.com/blogs/bezel-barrel/the-5-best-tips-for-authenticating-a-rolex-or-other-swiss-watch), [Watch Chest](https://watchchest.com/journal/verify-authentic-rolex-guide.html)
- Commercial photo/AI "legit check" services exist (e.g., LegitGrails, WatchScanning) - [LegitGrails](https://legitgrails.com/products/rolex-legit-check-service), [WatchScanning](https://www.watchscanning.com/authenticate/rolex/) - showing demand but also a liability-heavy niche.
- Brand-level CV precedent: HF Space trained on Chrono24 scraped images (ResNet50, 15 brands); notes Chrono24 images are professionally shot from similar angles (domain-gap risk for Instagram/phone photos). - [kevintang513/watch-watcher](https://github.com/kevintang513/watch-watcher)

### Inferences
- Realistic: "found on Instagram/in a shop window, what is it?", "which reference is the gift I received/box says X?", pre-purchase research (then link to ref page with price range and buying guide).
- Risky: "is this real?", valuation promises, "safe to buy" language. Use disclaimer + link to professional authentication; show "what to check" educational content instead of verdict.
- Input photos from phones, angles, wrists will differ from catalogue images; UI should request dial-forward, straight-on shots and show low-confidence states.

### Gaps
- Current r/rolex, r/Watches and WatchUSeek rules and actual user threads about ID tools not retrieved. No evidence on user demand for ID apps beyond commercial authentication services.

## 4. Legal/ethical: images and trademarks

### Takeaway
Descriptive/nominative use of the Rolex name to identify its products is generally defensible; copying Rolex.com photos/content is not allowed by its terms; implying affiliation or endorsement is the real risk. Not legal advice.

### Cited Findings
- Rolex.com terms: content/code may not be used other than as set out; marks may not be used in a confusing way without Rolex's written permission. - [Rolex terms of use](https://www.rolex.com/en-us/legal-notices/terms-of-use.html) (summary via search; page fetch 403)
- Nominative fair use: allowed when reasonably necessary to identify the owner's product and not suggesting sponsorship; fails if used to describe your own altered goods (Rolex v. BeckerTime) or implies endorsement. - [Fashion Law: Rolex resale fight](https://www.thefashionlaw.com/rolex-resale-fight-tests-limits-of-trademark-power-in-the-luxury-watch-market/), [Fashion Law: laCalifornienne](https://www.thefashionlaw.com/custom-watch-co-lacalifornienne-responds-to-rolex-counterfeit-case-claiming-fair-use/)
- First-sale doctrine protects resale of genuine goods, with limits for "materially different" goods. - [Fashion Law](https://www.thefashionlaw.com/rolex-resale-fight-tests-limits-of-trademark-power-in-the-luxury-watch-market/)
- Rolex actively sues online resellers over counterfeit/altered watches. - [Fashion Law](https://www.thefashionlaw.com/in-new-suit-rolex-accuses-online-retailers-of-selling-counterfeit-watches/)
- WatchBase treats its DB as protected under the Dutch Databases Act; reuse only as the terms allow. - [WatchBase terms via search summary](https://watchbase.com/terms) (fetch 403)
- A third-party page (rolex-config.pages.dev) shows an editorial-use notice pattern; not Rolex's position. - [rolex-config legal](https://rolex-config.pages.dev/legal)

### Inferences
- Portfolio safe pattern: a prominent "unofficial, not affiliated with or endorsed by Rolex" notice; use Rolex name only to identify; no Rolex logo/crown as branding; own or openly licensed images (user uploads, CC photos with attribution) and not scraped Rolex.com/Chrono24 images; no sale of watches; no authenticity guarantee.
- Training on scraped Chrono24 images carries ToS/copyright risk even for non-commercial; keep training data separate from displayed images.

### Gaps
- Chrono24 ToS and image licences not checked. No legal advice sought; no case about ID/portfolio sites found.

## 5. Free/open data sources

### Takeaway
No ready open Rolex spec+image dataset found. Wikimedia Commons has a small Rolex category; Wikidata has the company item but no watch-model items found; WatchBase is paid/restricted; small Roboflow/HF sets exist but are weak.

### Cited Findings
- Commons "Rolex watches" subcategory is small (~11 files in a mirror) and licences vary per file (e.g., a Day-Date dial photo is CC0). - [Commons mirror](https://download.osmand.net/wiki/Category:Rolex), [Commons file](https://wiki.riteme.site/wiki/File:Rolex_Day-Date_Lacquered_Stella_Dial.jpg)
- Wikidata: Rolex (Q62288) company item; no model-level items found. - [Wikidata](https://www.wikidata.org/wiki/Q62288)
- WatchBase: paid Data Feed API at api.watchbase.com/v1; 2017 pricing $0.25/watch call (may be outdated); a 30-day free trial existed in 2017. - [WatchBase Data Feed](https://datafeed.watchbase.com), [2017 post](https://watchbase.com/blog/2017/04/20/try-our-datafeed-api-free-for-30-days). A scraper exists on Apify but legality under terms unaddressed.
- Datasets: HF noxneural/watches_chrono24 (gated, Chrono24-scraped); Roboflow Universe "ROLEX" (55 images, detection); Nyckel brand classifier API (30 brands). - [HF](https://huggingface.co/datasets/noxneural/watches_chrono24/tree/main), [Roboflow](https://universe.roboflow.com/led-ovrap/rolex-bnb71), [Nyckel](https://nyckel.com/pretrained-classifiers/watch-brands)
- WatchCharts offers a B2B catalog/data product. - [WatchCharts B2B](https://watchcharts.com/b2b)

### Inferences
- Plan: hand-curate a spec JSON for the covered refs from manufacturer/primary facts (facts are not copyrightable, but wording/photos are); own-written descriptions; Commons photos per-file licence with attribution; user-upload for inference only.

### Gaps
- No Kaggle Rolex dataset found. Wikipedia "Rolex" model-list pages and Wikidata watch-model properties not checked. Licences of HF/Roboflow sets not verified. Reddit/forum content licence not examined.
