import json

# Market cap in $B, sourced companiesmarketcap.com (accessed July 2026) — real trillion/billion-scale
# figures for the "Data Hook" bar chart. Where standalone public market cap isn't available
# (private/subsidiary/conglomerate entities), we fall back to the existing DVA/Rev proxy and flag it.
MARKET_CAP_USD_B = {
    "NVIDIA":   5103,
    "TSMC":     2396,
    "SAMSUNGF": 1516,
    "AMD":       876.23,
    "ASML":      743.73,
    "INTELF":    673.43,
    "APPLMAT":   489.96,
    "LAMRES":    486.52,
    "ARM":       469.37,
    "KLA":       339.05,
    "QUALCOMM":  238.31,
    "TEL":       212.54,
    "ASE":        88.98,
    "CADENCE":   189.0,   # combined Cadence (~102B) + Synopsys (~87B) EDA duopoly, matches node's combined label
    "SMIC":       78.22,
    "AMKOR":      22.42,
    "TECHPROBE":  27.56,
    "FORMFACTOR": 11.65,
    "SUMCO":       9.22,
}
# Not independently public / not in semiconductor sector market cap list — DVA/Rev proxy retained
NO_MARKETCAP = {"SHINETSU", "JSR", "MERCKKG", "CHALCO"}

nodes = json.load(open('/home/claude/work/nodes_augmented.json'))
for n in nodes:
    if n['id'] in MARKET_CAP_USD_B:
        n['market_cap_usd_b'] = MARKET_CAP_USD_B[n['id']]
        n['financial_metric'] = 'market_cap'
    elif n['node_type'] == 'firm':
        n['market_cap_usd_b'] = None
        n['financial_metric'] = 'revenue_proxy'  # dva_usd_m used instead
    else:
        n['market_cap_usd_b'] = None
        n['financial_metric'] = 'dva'  # countries use DVA

json.dump(nodes, open('/home/claude/work/nodes_final.json', 'w'), indent=2)

# Quick print of what Section 1's bar chart will show, sorted by financial weight
def weight(n):
    if n.get('market_cap_usd_b'): return n['market_cap_usd_b'] * 1000  # to $M scale like dva
    return n.get('dva_usd_m', 0) or 0

ranked = sorted(nodes, key=lambda n: -weight(n))[:15]
for n in ranked:
    metric = n['financial_metric']
    val = n['market_cap_usd_b'] if n.get('market_cap_usd_b') else n.get('dva_usd_m',0)/1000
    unit = "B mkt cap" if metric=='market_cap' else ("B DVA" if metric=='dva' else "B rev(proxy)")
    print(f"{n['label']:<28}{val:>9.1f} {unit}")
