import tensorlayerx as tlx
import math

from gammagl.layers.conv import GCNConv


class Discriminator(tlx.nn.Module):
    def __init__(self, n_hid):
        super(Discriminator, self).__init__()

        init = tlx.nn.initializers.RandomUniform(-1.0 / math.sqrt(n_hid), 1.0 / math.sqrt(n_hid))
        # tlx dont support Variable in paddle backend
        # self.ww = tlx.Variable(init(shape=(n_hid, n_hid), dtype=tlx.float32), name="ww", trainable=True)

        self.fc = tlx.nn.Linear(in_features=n_hid, out_features=n_hid, W_init=init)

    def forward(self, feat, summary):
        feat = tlx.matmul(self.fc(feat), tlx.expand_dims(summary, -1))

        return feat


class GCN(tlx.nn.Module):
    def __init__(self, in_ft, out_ft, act, add_bias=True):
        super(GCN, self).__init__()
        self.conv = GCNConv(in_ft, out_ft, add_bias=add_bias)
        self.act = act


    def forward(self, feat, edge_index, edge_weight, num_nodes):
        x = self.conv(feat, edge_index, edge_weight, num_nodes)
        return self.act(x)


class DGIModel(tlx.nn.Module):
    """
    Deep Graph Infomax in DGL

    References
    ----------
    Papers: https://arxiv.org/abs/1809.10341
    Author's code: https://github.com/PetarV-/DGI
    """

    def __init__(self, in_feat, hid_feat, act):
        super(DGIModel, self).__init__()
        self.gcn = GCN(in_feat, hid_feat, act)
        self.disc = Discriminator(hid_feat)
        self.loss = tlx.losses.sigmoid_cross_entropy

    def forward(self, feat1, feat2, edge_index, edge_weight, num_nodes):
        pos = self.gcn(feat1, edge_index, edge_weight, num_nodes)
        neg = self.gcn(feat2, edge_index, edge_weight, num_nodes)

        summary = tlx.sigmoid(tlx.reduce_mean(pos, axis=0))

        pos = self.disc(pos, summary)
        neg = self.disc(neg, summary)

        pos_loss = self.loss(pos, tlx.ones_like(pos))
        neg_loss = self.loss(neg, tlx.zeros_like(neg))

        return pos_loss + neg_loss
