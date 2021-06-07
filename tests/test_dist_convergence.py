"""Distribution convergence and consistency tests for reversible ReCom."""
import os
import numpy as np
import pytest
import networkx as nx
from functools import partial
from collections import defaultdict
from gerrychain import Graph, GeographicPartition, MarkovChain
from gerrychain.accept import always_accept
from gerrychain.proposals import reversible_recom

NUM_STEPS = {4: 50000, 5: 10000}
EPSILON = {4: 0.1, 5: 1}

@pytest.fixture(params=[4, 5])
def enum_balanced_NxN(request):
    """Loads the enumeration of balanced NxN → N grid plans."""
    N = request.param
    path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'data', 'enum', f'{N}x{N}_all.txt'
    )

    with open(path) as f:
        raw_assignments = [[int(a) + 1 for a in line.split()]
                           for line in f.readlines()]
    graph = nx.grid_graph(dim=[N, N])
    for node in graph.nodes:
        graph.nodes[node]['population'] = 1

    assignments = [
        {node: a for node, a in zip(graph.nodes, assignment)}
        for assignment in raw_assignments
    ]
    partitions = [GeographicPartition(graph=graph, assignment=a) for a in assignments]
    return N, graph, partitions


def test_revrecom_dist(enum_balanced_NxN):
    N, graph, partitions_enum = enum_balanced_NxN
    st_counts = np.array(
        [np.prod([p.get_num_spanning_trees(dist) for dist in p.parts])
         for p in partitions_enum]
    )
    true_weights = {}
    for st_count, part in zip(st_counts, partitions_enum):
        # Partitions can be uniquely identified (up to labeling) by their cut edges.
        true_weights[tuple(sorted(part['cut_edges']))] = 1 / st_count

    # Run a reversible ReCom chain on the 5x5 grid.
    proposal = partial(
        reversible_recom,
        pop_col='population',
        pop_target=N,
        epsilon=0
    )
    num_steps = NUM_STEPS[N]
    chain = MarkovChain(
        proposal=proposal,
        accept=always_accept,
        initial_state=partitions_enum[0],
        total_steps=num_steps,
        constraints=[]
    )

    observed_freq = defaultdict(int)
    for part in chain:
        observed_freq[tuple(sorted(part['cut_edges']))] += 1

    true_vec = np.zeros(len(partitions_enum))
    observed_vec = np.zeros(len(partitions_enum))
    for idx, (cut_edges, weight) in enumerate(true_weights.items()):
        true_vec[idx] = weight
        observed_vec[idx] = observed_freq[cut_edges]
    true_vec /= true_vec.sum()
    observed_vec /= observed_vec.sum()

    # Compute bin distances.
    distance = np.linalg.norm(true_vec - observed_vec)
    print(true_vec)
    print(observed_vec)
    print('distance is', distance)
    assert distance < 0.001
