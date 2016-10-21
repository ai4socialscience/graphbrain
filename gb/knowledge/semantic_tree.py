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


from __future__ import print_function
from asciitree import LeftAligned
from collections import OrderedDict


LEAF = 0
NODE = 1


class Position(object):
    LEFT, RIGHT = range(2)


class Elements(object):
    def __init__(self):
        self.cur_id = 0
        self.table = {}

    def get(self, elem_id):
        if elem_id is None:
            return None
        return self.table[elem_id]

    def set(self, elem_id, elem):
        elem.id = elem_id
        self.table[elem_id] = elem

    def add(self, elem):
        self.set(self.cur_id, elem)
        self.cur_id += 1

    def create_leaf(self, pivot):
        leaf = Leaf(pivot)
        leaf.elems = self
        self.add(leaf)
        return leaf.id

    def create_node(self, base_token, children=None, placeholder=False):
        node = Node(base_token, children, placeholder)
        node.elems = self
        node.init_layers()
        self.add(node)
        return node.id

    def enclose(self, entity):
        node_id = entity.id
        self.add(entity)
        node = self.get(self.create_node(entity.base_token, [entity.id]))
        self.set(node_id, node)
        return node

    def disenclose(self, node):
        assert(node.is_node())
        assert(len(node.children) > 0)
        entity_id = node.id
        inner_entity = self.get(node.children[0])
        self.set(entity_id, inner_entity)

    def create_placeholder(self):
        return self.create_node(None, None, True)


class Element(object):
    def __init__(self, base_token):
        self.type = None
        self.base_token = base_token
        self.id = None
        self.elems = None

    def is_leaf(self):
        return self.type == LEAF

    def is_node(self):
        return self.type == NODE

    def apply_layers(self):
        # if not implemented, do nothing.
        pass

    def remove_redundant_nesting(self):
        # if not implemented, do nothing.
        pass

    def root_token(self):
        # throw exception
        pass

    def append_child(self, elem_id):
        # throw exception
        pass

    def append_to_root(self, elem_id, pos):
        # throw exception
        pass

    def apply_modifier(self, elem_id):
        # throw exception
        pass

    def label_tree(self):
        # throw exception
        pass

    def str_with_layers(self):
        # throw exception
        pass


class Leaf(Element):
    def __init__(self, pivot):
        super(Leaf, self).__init__(pivot)
        self.type = LEAF
        self.pivot = pivot
        self.left = []
        self.right = []

    # override
    def root_token(self):
        return self.pivot

    # override
    def append_child(self, elem_id):
        node = self.elems.enclose(self)
        node.append_child(elem_id)

    # override
    def append_to_root(self, elem_id, pos):
        node = self.elems.enclose(self)
        return node.append_to_root(elem_id, pos)

    # override
    def apply_modifier(self, elem_id):
        node = self.elems.enclose(self)
        return node.apply_modifier(elem_id)

    # override
    def label_tree(self):
        return '* %s' % self.base_token.chunk_str(), OrderedDict([])

    # override
    def str_with_layers(self):
        return str(self)

    def __str__(self):
        words = [token.word for token in self.left]
        words.append(self.pivot.word)
        words += [token.word for token in self.right]
        return '_'.join(words)


class Node(Element):
    def __init__(self, base_token, children=None, placeholder=False):
        super(Node, self).__init__(base_token)
        self.type = NODE
        if children is None:
            self.children = []
        else:
            self.children = children
        self.placeholder = placeholder
        self.layers = []
        self.layer_id = -1

    def init_layers(self):
        if not self.placeholder:
            self.layer_id = self.elems.create_placeholder()

    def get_child(self, i):
        return self.elems.get(self.children[i])

    def set_child(self, i, elem_id):
        self.children[i] = elem_id

    def new_layer(self):
        if not self.elems.get(self.layer_id).placeholder:
            self.layers.append(self.layer_id)
            self.layer_id = self.elems.create_placeholder()

    def apply_layer(self, entity, layer):
        for i in range(len(layer.children)):
            if layer.get_child(i).is_node():
                if layer.get_child(i).placeholder:
                    child_id = self.elems.create_node(entity.base_token, entity.children)
                    child = self.elems.get(child_id)
                    if child.is_singleton():
                        child_id = child.children[0]
                    layer.set_child(i, child_id)
                    return
                self.apply_layer(entity, layer.get_child(i))

    def apply_layers(self):
        self.layers.reverse()
        prev_layer = self
        for layer_id in self.layers:
            layer = self.elems.get(layer_id)
            self.apply_layer(prev_layer, layer)
            prev_layer = layer
        self.children = prev_layer.children
        self.layers = []

    def is_singleton(self):
        return len(self.children) == 1

    def is_node_singleton(self):
        if not self.is_singleton():
            return False
        child = self.elems.get(self.children[0])
        return child.is_node()

    # TODO: hack
    def root(self):
        if len(self.children) > 0:
            node0 = self.get_child(0)
            if node0.is_leaf():
                return node0
            else:
                return node0.root()
        else:
            raise IndexError('Requesting root on an empty Node')

    # override
    def root_token(self):
        return self.root().pivot

    # override
    def append_child(self, elem_id):
        self.children.append(elem_id)

    # override
    def append_to_root(self, elem_id, pos):
        if len(self.children) > 0:
            if self.get_child(0).is_leaf():
                self.set_child(0, self.elems.enclose(self.get_child(0)).id)
            if pos == Position.RIGHT:
                self.elems.get(elem_id).parent = self
                self.get_child(0).children.append(elem_id)
            else:
                self.elems.get(elem_id).parent = self
                self.get_child(0).children.insert(0, elem_id)
        else:
            raise IndexError('Requesting root on an empty Node')
        return self

    # override
    def apply_modifier(self, elem_id):
        elem = self.elems.get(elem_id)
        if elem.is_leaf():
            rel = elem_id
            rest = []
        else:
            rel = elem.children[0]
            rest = elem.children[1:]
        self.layer_id = self.elems.create_node(elem.base_token, [rel, self.layer_id] + rest)
        return self

    # override
    def remove_redundant_nesting(self):
        for child_id in self.children:
            child = self.elems.get(child_id)
            child.remove_redundant_nesting()
        if self.is_node_singleton():
            self.elems.disenclose(self)

    def label(self):
        chunk_str = 'N/A'
        if self.base_token is not None:
            chunk_str = self.base_token.chunk_str()
        return '[%s] {%s}' % (str(self.get_child(0)), chunk_str)

    # override
    def label_tree(self):
        children = [self.elems.get(child_id).label_tree() for child_id in self.children]
        return self.label(), OrderedDict(children)

    def print_tree(self):
        label, children = self.label_tree()
        tr = LeftAligned()
        print(tr({label: children}))

    # override
    def str_with_layers(self):
        layers = [str(self.elems.get(layer)) for layer in self.layers]
        layers_str = ' '.join(layers)
        return '%s {%s}' % (str(self), layers_str)

    def __str__(self):
        if self.placeholder:
            return '[*]'
        else:
            strs = [str(self.elems.get(child_id)) for child_id in self.children]
            return '(%s)' % ' '.join(strs)
