# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2022/05/14 21:54
# @Author  : clear
# @FileName: test_agnn_conv.py

import tensorlayerx as tlx
from gammagl.layers.conv import AGNNConv

def test_agnn_conv():
    x = tlx.random_normal(shape=(4, 64))
    edge_index = tlx.convert_to_tensor([[0, 0, 0, 1, 2, 3], [1, 2, 3, 0, 0, 0]])

    conv = AGNNConv(in_channels=64, edge_index=edge_index, num_nodes=4)
    out = conv(x)
    assert out.shape == (4, 64)

test_agnn_conv()
