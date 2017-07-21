#   Copyright (c) 2016 CNRS - Centre national de la recherche scientifique.
#   All rights reserved.
#
#   Written by Telmo Menezes <telmo@telmomenezes.com>
#
#   This file is part of GraphBrain.
#
#   GraphBrain is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   GraphBrain is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with GraphBrain.  If not, see <http://www.gnu.org/licenses/>.


import itertools
import igraph
import gb.tools.json as json_tools
import gb.hypergraph.symbol as sym
import gb.hypergraph.edge as ed
import gb.nlp.parser as par


MAX_PROB = -12


class Graph(object):
    def __init__(self, parser, claims):
        self.parser = parser
        self.graph = None
        self.edges = {}
        self.vertices = set()
        self.init_graph(claims)

    def init_graph(self, claims):
        for claim in claims:
            self.add_claim(claim)
        self.graph = igraph.Graph()  #(directed=True)
        self.graph.add_vertices(list(self.vertices))
        self.vertices = None
        self.graph.add_edges(self.edges.keys())
        self.graph.es['weight'] = list(self.edges.values())
        self.edges = None

    # orig --[has part]--> targ
    def add_link(self, orig, targ):
        if (orig, targ) not in self.edges:
            self.edges[(orig, targ)] = 0.
        self.edges[(orig, targ)] += 1.

    def edge2str(self, edge):
        s = ed.edge2str(edge, namespaces=False)
        if sym.is_edge(edge):
            return s

        if s[0] == '+':
            s = s[1:]

        if len(s) == 0:
            return None

        if not s[0].isalnum():
            return None

        word = self.parser.make_word(s)
        if word.prob < MAX_PROB:
            return s

        return None

    def add_claim(self, edge):
        orig = self.edge2str(edge)
        if not orig:
            return
        self.vertices.add(orig)
        if sym.is_edge(edge):
            elements = []
            # links from part to whole
            for element in edge:
                targ = self.edge2str(element)
                if not targ:
                    return
                elements.append(targ)
                self.vertices.add(targ)
                self.add_link(orig, targ)
                self.add_claim(element)

            # links between peers
            combs = itertools.combinations(elements, 2)
            for comb in combs:
                self.add_link(*comb)

    def normalize_graph(self):
        for orig in self.graph.vs:
            edges = self.graph.incident(orig.index, mode='in')
            total = sum([self.graph.es[edge]['weight'] for edge in edges])
            for edge in edges:
                self.graph.es[edge]['weight'] = self.graph.es[edge]['weight'] / total

    def find_edge(self, orig, targ):
        try:
            orig_id = self.graph.vs.find(orig).index
            targ_id = self.graph.vs.find(targ).index
            return self.graph.es.find(_between=((orig_id,), (targ_id,)))
        except:
            return None

    def similarity(self, edge1, edge2):
        e1 = ed.edge2str(edge1, namespaces=False)
        e2 = ed.edge2str(edge2, namespaces=False)
        edge = self.find_edge(e1, e2)
        if edge:
            return edge['weight']
        edge = self.find_edge(e2, e1)
        if edge:
            return edge['weight']
        return 0.


if __name__ == '__main__':
    print('creating parser...')
    par = par.Parser()
    print('parser created.')

    # read data
    # edge_data = json_tools.read('edges_similar_concepts.json')
    edge_data = json_tools.read('all.json')

    # build full edges list
    full_edges = []
    for it in edge_data:
        full_edges.append(ed.without_namespaces(ed.str2edge(it['edge'])))

    # build graph
    g = Graph(par, full_edges)
    # g.normalize_graph()

    print(g.similarity('hillary', ['+', 'hillary', 'clinton']))

    pr = g.graph.pagerank(weights='weight')
    pr_pairs = [(g.graph.vs[i]['name'], pr[i]) for i in range(len(pr))]
    pr_pairs = sorted(pr_pairs, key=lambda x: x[1], reverse=True)

    remaining_edges = full_edges[:]
    covered = set()
    for pr_pair in pr_pairs:
        label = pr_pair[0]
        pr = pr_pair[1]
        edge = ed.str2edge(label)
        count = 0
        new_remaining_edges = []
        for full_edge in remaining_edges:
            if ed.contains(full_edge, edge, deep=True):
                count += 1
                covered.add(ed.edge2str(full_edge, namespaces=False))
            else:
                new_remaining_edges.append(full_edge)
        remaining_edges = new_remaining_edges
        print('%s [%s]{%s} %.2f%% %s' % (label, count, len(covered),
                                         (float(len(covered)) / float(len(full_edges))) * 100., pr))

    # community detection
    # comms = igraph.Graph.community_multilevel(g.graph, weights='weight', return_levels=False)
    # print(comms)
