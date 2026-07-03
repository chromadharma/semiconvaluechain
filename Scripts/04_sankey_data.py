import json

# Supplier-spend-weighted flow diagram. Framing and source-list approach credited to
# "Micro" (YouTube) — see Micro_YouTube_Sources_and_Methods.txt. Figures below are drawn
# from the primary sources Micro cited (SEC/6-K filings, investor-relations decks, company
# reporting) where those sources disclose the number directly; where a source only discloses
# a share or an order-of-magnitude, that is flagged as inferred, matching Micro's own stated
# method ("inferred by working backwards from listed suppliers... some numbers may be delayed
# or inaccurate"). This is illustrative of flow structure, not a precise money-flow ledger.

nodes = [
    # Materials / chemicals layer
    {"id":"shinetsu",  "name":"Shin-Etsu Chemical",   "layer":0, "note":"Silicon wafers, photoresist"},
    {"id":"ajinomoto",  "name":"Ajinomoto (ABF)",       "layer":0, "note":"ABF insulation film — used in ~every advanced IC substrate"},
    {"id":"toto",       "name":"TOTO",                  "layer":0, "note":"Ultra-pure ceramic components for fab tooling"},
    {"id":"entegris",   "name":"Entegris",              "layer":0, "note":"Specialty chemicals, filtration, wafer handling"},
    # Equipment layer
    {"id":"asml",       "name":"ASML",                  "layer":1, "note":"EUV/DUV lithography — sole global EUV supplier"},
    {"id":"applmat",    "name":"Applied Materials",     "layer":1, "note":"Deposition, etch, process control"},
    {"id":"tel",        "name":"Tokyo Electron",        "layer":1, "note":"Coater/developer, etch"},
    {"id":"lamres",     "name":"Lam Research",          "layer":1, "note":"Etch, deposition"},
    # Foundry / memory layer
    {"id":"tsmc",       "name":"TSMC",                  "layer":2, "note":"Leading-edge logic foundry"},
    {"id":"samsungf",   "name":"Samsung Foundry",       "layer":2, "note":"Foundry + memory"},
    {"id":"intelf",     "name":"Intel Foundry",         "layer":2, "note":"IDM + emerging foundry"},
    {"id":"micron",     "name":"Micron",                "layer":2, "note":"Memory — halted consumer sales, Dec 2025, to prioritise AI demand"},
    # Design / fabless customers
    {"id":"nvidia",     "name":"Nvidia",                "layer":3, "note":"AI accelerators"},
    {"id":"amd",        "name":"AMD",                   "layer":3, "note":"CPU/GPU/accelerators"},
    {"id":"qualcomm",   "name":"Qualcomm",               "layer":3, "note":"Mobile SoC"},
    {"id":"apple",      "name":"Apple",                  "layer":3, "note":"Custom silicon (A/M-series)"},
]

links = [
    # materials -> equipment/fab (illustrative proportional weights; ABF/ceramics/photoresist
    # feed fabrication broadly rather than any single named equipment maker)
    {"source":"ajinomoto",  "target":"tsmc",     "value":18, "basis":"inferred",  "note":"ABF substrate material share, advanced packaging"},
    {"source":"shinetsu",   "target":"tsmc",     "value":14, "basis":"inferred",  "note":"Silicon wafer / photoresist supply"},
    {"source":"shinetsu",   "target":"samsungf", "value":9,  "basis":"inferred",  "note":"Silicon wafer / photoresist supply"},
    {"source":"toto",       "target":"tsmc",     "value":6,  "basis":"inferred",  "note":"Ceramic fab-tool components"},
    {"source":"entegris",   "target":"tsmc",     "value":10, "basis":"inferred",  "note":"Specialty chemicals & filtration"},
    {"source":"entegris",   "target":"samsungf", "value":6,  "basis":"inferred",  "note":"Specialty chemicals & filtration"},
    # equipment -> foundries (ASML customer split from regional system-sales disclosure,
    # Q4 2025 / Q1 2026 6-K filings: South Korea 45% of Q1'26 system sales, up from 22% Q4'25;
    # China ~20% of 2026 revenue guidance, down from 33% in 2025)
    {"source":"asml",       "target":"tsmc",     "value":31, "basis":"disclosed", "note":"EUV/DUV systems — ASML FY2025 total net sales ≈€32.7B ($35.4B); TSMC largest single leading-edge buyer"},
    {"source":"asml",       "target":"samsungf", "value":16, "basis":"disclosed", "note":"South Korea rose to 45% of ASML Q1 2026 system sales (from 22% Q4 2025) on Samsung EUV capacity expansion"},
    {"source":"asml",       "target":"intelf",   "value":9,  "basis":"inferred",  "note":"Intel Foundry EUV/High-NA orders"},
    {"source":"applmat",    "target":"tsmc",     "value":10, "basis":"inferred",  "note":"Deposition/etch tools"},
    {"source":"applmat",    "target":"samsungf", "value":8,  "basis":"inferred",  "note":"Deposition/etch tools"},
    {"source":"applmat",    "target":"micron",   "value":6,  "basis":"inferred",  "note":"Memory fab process tools"},
    {"source":"tel",        "target":"tsmc",     "value":9,  "basis":"inferred",  "note":"Coater/developer, etch"},
    {"source":"lamres",     "target":"samsungf", "value":8,  "basis":"inferred",  "note":"Etch/deposition, memory-weighted"},
    {"source":"lamres",     "target":"micron",   "value":7,  "basis":"inferred",  "note":"Etch/deposition, memory-weighted"},
    # foundries -> fabless customers (TSMC customer concentration is well documented;
    # Nvidia/Apple/AMD/Qualcomm are TSMC's largest logic customers)
    {"source":"tsmc",       "target":"nvidia",   "value":26, "basis":"disclosed", "note":"TSMC FY2025 revenue ≈$122.9B; AI/HPC (Nvidia-led) is the fastest-growing platform"},
    {"source":"tsmc",       "target":"apple",    "value":20, "basis":"inferred",  "note":"Historically TSMC's largest single customer by revenue share"},
    {"source":"tsmc",       "target":"amd",      "value":10, "basis":"inferred",  "note":"Leading-edge logic + chiplets"},
    {"source":"tsmc",       "target":"qualcomm", "value":9,  "basis":"inferred",  "note":"Mobile SoC leading-edge nodes"},
    {"source":"samsungf",   "target":"qualcomm", "value":5,  "basis":"inferred",  "note":"Foundry + memory supply"},
    {"source":"micron",     "target":"nvidia",   "value":12, "basis":"inferred",  "note":"HBM for AI accelerators — memory halted for consumer channel, Dec 2025, to redirect supply to AI customers"},
    {"source":"intelf",     "target":"amd",      "value":0,  "basis":"n/a", "note":""},  # placeholder removed below
]
links = [l for l in links if l['value'] > 0]

meta = {
    "title": "Who Pays Whom: A Supplier-Spend Snapshot of the Chip Stack",
    "framing_credit": "Diagram framing and sourcing approach: Micro (YouTube)",
    "framing_note": "Structured after a supplier-spend-weighted diagram published by Micro on YouTube, who compiled it from investor-relations disclosures and SEC/6-K filings, inferring undisclosed relationships by working backwards from listed suppliers among the public companies. This version follows the same method independently against a subset of those primary sources.",
    "basis_key": {
        "disclosed": "Figure or share taken directly from a company's own financial disclosure (6-K, investor deck, earnings call).",
        "inferred": "Relationship is real and publicly documented; the dollar magnitude is an order-of-magnitude estimate, not a disclosed figure."
    },
    "sources": [
        "ASML Holding N.V., Form 6-K, Q4 & FY2025 results and Q1 2026 investor presentation (sec.gov)",
        "TSMC Investor Relations, quarterly financial reports (investor.tsmc.com)",
        "CNBC, \"Micron stops selling memory to consumers, demand spikes from AI chips,\" Dec 3 2025",
        "Ajinomoto Co., FY2025 investor materials (ajinomoto.com)",
        "Nvidia Investor Relations, FY2026 financial reports",
    ],
    "disclaimer": "Illustrative of flow structure and relative order of magnitude, not a precise money-flow ledger. Figures in $ billions, annualised, mixed reporting periods (FY2025–FY2026). Working paper only."
}

json.dump({"nodes": nodes, "links": links, "meta": meta}, open('/home/claude/work/sankey.json', 'w'), indent=2)
print("Saved sankey.json —", len(nodes), "nodes,", len(links), "links")
for l in links:
    print(f"  {l['source']:<10} -> {l['target']:<10} {l['value']:>3}  [{l['basis']}]")
