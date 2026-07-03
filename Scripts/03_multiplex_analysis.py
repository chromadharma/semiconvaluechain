import json

nodes = json.load(open('/mnt/user-data/uploads/nodes.json'))
meta  = json.load(open('/mnt/user-data/uploads/meta.json'))
L = len(meta['layers'])  # 6
layer_ids = [l['id'] for l in meta['layers']]

def compute_multiplex(n):
    bcs = [n.get(f'bc_l{lid}', 0) or 0 for lid in layer_ids]
    O = sum(bcs)  # overall multiplex centrality (sum of per-layer BC)
    if O == 0:
        return 0.0, 0.0, 0
    shares_sq = sum((b / O) ** 2 for b in bcs)
    P = (L / (L - 1)) * (1 - shares_sq)  # participation coefficient, 0 (mono-layer) .. ~1 (evenly spread)
    n_active = sum(1 for b in bcs if b > 0)
    return round(O, 4), round(P, 4), n_active

for n in nodes:
    O, P, n_active = compute_multiplex(n)
    n['omc'] = O                  # Overall Multiplex Centrality
    n['participation'] = P        # Multiplex Participation Coefficient (Battiston et al. 2014)
    n['n_layers_active'] = n_active

# Rank by OMC to see top cross-layer players
ranked = sorted(nodes, key=lambda n: -n['omc'])
print(f"{'ID':<12}{'Type':<8}{'OMC':>7}{'Particip.':>11}{'#Layers':>9}")
for n in ranked[:20]:
    print(f"{n['id']:<12}{n['node_type']:<8}{n['omc']:>7}{n['participation']:>11}{n['n_layers_active']:>9}")

json.dump(nodes, open('/home/claude/work/nodes_augmented.json', 'w'), indent=2)
print("\nSaved nodes_augmented.json with omc / participation / n_layers_active fields")
