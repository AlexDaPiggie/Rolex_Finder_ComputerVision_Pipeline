# Variant matching on real photos

31 real photos (Wikimedia Commons and Flickr via Openverse) whose title or file name names a reference number that belongs to exactly one catalog variant. Run through the live API (2026-11-17). The variant head was trained on retailer photos only, so none of these were seen. Labels come from titles, so a few may be wrong.

| Measure | Result |
|---|---|
| Family right | 29 of 31 |
| Right variant is the top pick (end to end) | 15 of 31 (48%) |
| Right variant in the top 3 (end to end) | 27 of 31 (87%) |
| Top pick, family right | 15 of 29 |
| Top 3, family right | 27 of 29 |

Compare: retailer test photos, family known, top-1 97.8% and top-3 99.6%. Studio photos are far easier.

Most misses are near-twins in the catalog, not wild errors:
- Paul Newman Daytona (6263, 6265) is read as the steel-bezel Daytona (4 photos).
- GMT-Master Pepsi (1675) is read as the regular GMT (3 photos).
- Datejust fluted is read as palm, MOP or champagne (3 photos).
- The Batman GMT is read as Bruce Wayne, which is the same look.

So the top-3 list is the number to trust. Small sample (31): treat the percentages as rough.
