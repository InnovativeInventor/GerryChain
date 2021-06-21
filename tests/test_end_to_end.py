from gerrychain.chain import MarkovChain
from gerrychain import Graph, Partition, Election
from gerrychain.updaters import Tally, cut_edges
from gerrychain.constraints import single_flip_contiguous
from gerrychain.proposals import propose_random_flip
from gerrychain.accept import always_accept
import pytest

def test_end_to_end(benchmark):
    @benchmark
    def benchmark():
        graph = Graph.from_json("./tests/data/PA_VTDs.json")

        election = Election("SEN12", {"Dem": "USS12D", "Rep": "USS12R"})

        initial_partition = Partition(
            graph,
            assignment="CD_2011",
            updaters={
                "cut_edges": cut_edges,
                "population": Tally("TOTPOP", alias="population"),
                "SEN12": election
            }
        )

        chain = MarkovChain(
            proposal=propose_random_flip,
            constraints=[single_flip_contiguous],
            accept=always_accept,
            initial_state=initial_partition,
            total_steps=100000
        )
