# Variant matching benchmark

743 retailer test photos whose file name names a reference number that belongs to exactly one catalog variant. Family is given (oracle), so this measures the CLIP text-prompt step only. Dial crops, as the site uses them. Labels come from file names, so a few are wrong. Studio photos, so real photos will score lower.

**Top-1: 53.7%** (random guess 17.8%). **Top-3: 87.9%** (random guess 52.2%).

| Family | Photos | Variants | Top-1 | Top-3 |
|---|---|---|---|---|
| airking | 124 | 4 | 71% | 100% |
| cellini | 66 | 11 | 29% | 52% |
| datejust | 231 | 6 | 42% | 96% |
| daytona | 48 | 9 | 52% | 69% |
| explorer | 40 | 5 | 100% | 100% |
| gmt_master | 18 | 10 | 28% | 72% |
| milgauss | 8 | 3 | 75% | 100% |
| oysterquartz | 20 | 2 | 35% | 100% |
| president | 55 | 6 | 69% | 98% |
| sea_dweller | 16 | 5 | 69% | 100% |
| submariner | 54 | 8 | 24% | 48% |
| turn_o_graph | 42 | 5 | 93% | 100% |
| yacht_master | 21 | 12 | 52% | 100% |

Most common mistakes (true variant -> predicted):

- datejust_champagne -> datejust_fluted: 100
- airking_classing_fluted -> airking_classic_smooth: 35
- submariner_black_date -> submariner_comex: 35
- daytona_steel_bezel -> daytona_two_tone: 16
- cellini_cestello -> cellini_classic_round: 13
- oysterquartz_datejust -> oysterquartz_day_date: 13
- cellini_danaos -> cellini_classic_round: 11
- datejust_smooth -> datejust_fluted: 11
- datejust_mop -> datejust_fluted: 9
- gmt_root_beer -> gmt_yellow_gold: 9
