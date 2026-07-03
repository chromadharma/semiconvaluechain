import json, random
import networkx as nx

nodes = json.load(open('/mnt/user-data/uploads/nodes.json'))
edges = json.load(open('/mnt/user-data/uploads/edges.json'))
meta  = json.load(open('/mnt/user-data/uploads/meta.json'))

node_ids = [n['id'] for n in nodes]
node_by_id = {n['id']: n for n in nodes}

# Build aggregate directed multigraph across all layers -> collapse to simple undirected
# graph for connectivity analysis (standard for robustness/percolation studies,
# consistent with the Itoh et al. methodology already used in AviationNet).
G = nx.Graph()
G.add_nodes_from(node_ids)
for e in edges:
    if e['source'] in node_by_id and e['target'] in node_by_id:
        G.add_edge(e['source'], e['target'])

N = G.number_of_nodes()
print("Aggregate simple graph: N =", N, "E =", G.number_of_edges())

def giant_component_fraction(H):
    if H.number_of_nodes() == 0:
        return 0.0
    comps = list(nx.connected_components(H))
    if not comps:
        return 0.0
    return max(len(c) for c in comps) / N

# ---- Targeted attack: remove nodes in descending order of betweenness centrality,
# RECALCULATED after each removal (the harder, more realistic attack scenario) ----
def targeted_attack_recalculated(G, steps=None):
    H = G.copy()
    order_removed = []
    results = [{"frac_removed": 0.0, "giant_frac": giant_component_fraction(H)}]
    total = H.number_of_nodes()
    n_steps = steps or total - 1
    for i in range(n_steps):
        if H.number_of_nodes() <= 1:
            break
        bc = nx.betweenness_centrality(H, normalized=True)
        if not bc:
            break
        target = max(bc, key=bc.get)
        H.remove_node(target)
        order_removed.append(target)
        frac = (i + 1) / total
        results.append({"frac_removed": round(frac, 4), "giant_frac": giant_component_fraction(H), "removed": target})
    return results, order_removed

# ---- Random failure: remove nodes in random order, averaged over multiple trials ----
def random_failure(G, trials=200):
    total = G.number_of_nodes()
    all_ids = list(G.nodes())
    accum = [0.0] * total  # accum[i] = sum of giant_frac after i removals, across trials
    accum[0] = giant_component_fraction(G) * trials
    for t in range(trials):
        order = all_ids[:]
        random.shuffle(order)
        H = G.copy()
        for i, nid in enumerate(order):
            if H.number_of_nodes() <= 1:
                # once graph is essentially gone, remaining giant_frac ~ 1/N or 0
                for j in range(i+1, total):
                    accum[j] += giant_component_fraction(H)
                break
            H.remove_node(nid)
            accum[i+1] += giant_component_fraction(H)
    return [{"frac_removed": round(i/total, 4), "giant_frac": accum[i]/trials} for i in range(total)]

print("Running targeted attack (recalculated betweenness)...")
targeted_results, removal_order = targeted_attack_recalculated(G)
print("Top 10 removal order (by recalculated BC):", removal_order[:10])

print("Running random failure simulation (200 trials)...")
random_results = random_failure(G, trials=200)

out = {
    "n_nodes": N,
    "n_edges": G.number_of_edges(),
    "targeted": targeted_results,
    "random": random_results,
    "removal_order_top15": removal_order[:15],
}
json.dump(out, open('/home/claude/work/percolation.json', 'w'), indent=2)
print("Saved percolation.json")

# Quick summary stat: fraction removed for giant component to drop below 50%
def frac_at_threshold(results, thresh=0.5):
    for r in results:
        if r['giant_frac'] < thresh:
            return r['frac_removed']
    return None

print("Targeted: giant component <50% after removing", frac_at_threshold(targeted_results), "of nodes")
print("Random:   giant component <50% after removing", frac_at_threshold(random_results), "of nodes")
