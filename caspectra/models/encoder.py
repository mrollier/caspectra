"""Encoders that map a spacetime diagram to a feature vector (BUILD_BRIEF.md §3.4).

Two encoders are provided:

* :class:`ResNet18Encoder` — a ResNet-18 adapted to a single input channel,
  with a configurable width, stem, and normalisation layer.
* :class:`SmallCNNEncoder` — a light custom CNN (~1M params) as an ablation
  alternative.

Both expose ``.embedding_dim`` and ``forward(x) -> (B, embedding_dim)``.

**Normalisation (M4-specific):** at 128x128 on unified memory the batch may be
forced below 256, where BatchNorm degrades and can destabilise BYOL. The
default is therefore **GroupNorm**; BatchNorm is selectable and the choice is
recorded in the config.
"""

from __future__ import annotations

from collections.abc import Callable

import torch
import torch.nn as nn
from torchvision.models.resnet import BasicBlock, conv1x1

__all__ = ["ResNet18Encoder", "SmallCNNEncoder", "AntiCheatCNN", "make_norm_layer"]

# A norm factory takes a channel count and returns a normalisation module.
NormFactory = Callable[[int], nn.Module]


def make_norm_layer(kind: str, num_groups: int = 8) -> NormFactory:
    """Return a factory ``num_channels -> nn.Module`` for the chosen norm.

    ``kind`` is ``"group"`` (default elsewhere) or ``"batch"``. For GroupNorm
    the requested ``num_groups`` is reduced to the largest divisor of the
    channel count so it is always valid.
    """
    if kind == "batch":
        return lambda num_channels: nn.BatchNorm2d(num_channels)
    if kind == "group":

        def factory(num_channels: int) -> nn.Module:
            groups = num_groups
            while num_channels % groups != 0 and groups > 1:
                groups -= 1
            return nn.GroupNorm(groups, num_channels)

        return factory
    raise ValueError(f"Unknown norm_layer {kind!r}; expected 'group' or 'batch'.")


class ResNet18Encoder(nn.Module):
    """ResNet-18 backbone producing a global-average-pooled feature vector.

    Parameters
    ----------
    width_multiplier:
        Scales all channel widths (default 1.0 -> 512-d output; 0.5 gives a
        lighter, less rule-memorising 256-d variant).
    small_input:
        When True (use only for grid_size <= 64 smoke tests) the 7x7/stride-2
        stem is replaced by a 3x3/stride-1 conv and the initial max-pool is
        dropped. At the default grid_size 128 keep this False (ImageNet stem).
    norm_layer:
        ``"group"`` (default) or ``"batch"``.
    in_channels:
        Number of input channels (1 for binary diagrams).
    """

    def __init__(
        self,
        width_multiplier: float = 1.0,
        small_input: bool = False,
        norm_layer: str = "group",
        num_groups: int = 8,
        in_channels: int = 1,
    ) -> None:
        super().__init__()
        norm = make_norm_layer(norm_layer, num_groups)
        base = int(64 * width_multiplier)
        widths = [base, base * 2, base * 4, base * 8]
        self.embedding_dim = widths[3] * BasicBlock.expansion

        # Stem.
        if small_input:
            self.conv1 = nn.Conv2d(
                in_channels, base, kernel_size=3, stride=1, padding=1, bias=False
            )
            self.maxpool: nn.Module = nn.Identity()
        else:
            self.conv1 = nn.Conv2d(
                in_channels, base, kernel_size=7, stride=2, padding=3, bias=False
            )
            self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        self.bn1 = norm(base)
        self.relu = nn.ReLU(inplace=True)

        # Residual stages (ResNet-18 = two BasicBlocks per stage).
        inplanes = base
        self.layer1, inplanes = self._make_stage(inplanes, widths[0], 2, 1, norm)
        self.layer2, inplanes = self._make_stage(inplanes, widths[1], 2, 2, norm)
        self.layer3, inplanes = self._make_stage(inplanes, widths[2], 2, 2, norm)
        self.layer4, inplanes = self._make_stage(inplanes, widths[3], 2, 2, norm)
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))

        self._init_weights()

    @staticmethod
    def _make_stage(
        inplanes: int, planes: int, blocks: int, stride: int, norm: NormFactory
    ) -> tuple[nn.Sequential, int]:
        downsample = None
        out_planes = planes * BasicBlock.expansion
        if stride != 1 or inplanes != out_planes:
            downsample = nn.Sequential(conv1x1(inplanes, out_planes, stride), norm(out_planes))
        layers = [BasicBlock(inplanes, planes, stride, downsample, norm_layer=norm)]
        for _ in range(1, blocks):
            layers.append(BasicBlock(out_planes, planes, norm_layer=norm))
        return nn.Sequential(*layers), out_planes

    def _init_weights(self) -> None:
        for module in self.modules():
            if isinstance(module, nn.Conv2d):
                nn.init.kaiming_normal_(module.weight, mode="fan_out", nonlinearity="relu")
            elif isinstance(module, (nn.BatchNorm2d, nn.GroupNorm)):
                nn.init.constant_(module.weight, 1)
                nn.init.constant_(module.bias, 0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.relu(self.bn1(self.conv1(x)))
        x = self.maxpool(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.avgpool(x)
        return torch.flatten(x, 1)


class SmallCNNEncoder(nn.Module):
    """A light 5-layer CNN alternative (~1M params).

    Uses global average pooling so it accepts any (square) input size.
    """

    def __init__(
        self,
        embedding_dim: int = 256,
        norm_layer: str = "group",
        num_groups: int = 8,
        in_channels: int = 1,
    ) -> None:
        super().__init__()
        self.embedding_dim = embedding_dim
        norm = make_norm_layer(norm_layer, num_groups)
        channels = [32, 64, 128, 256]

        def block(c_in: int, c_out: int) -> nn.Sequential:
            return nn.Sequential(
                nn.Conv2d(c_in, c_out, kernel_size=3, stride=1, padding=1, bias=False),
                norm(c_out),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(2),
            )

        c_prev = in_channels
        stages = []
        for c in channels:
            stages.append(block(c_prev, c))
            c_prev = c
        self.features = nn.Sequential(*stages)
        # 1x1 projection to the requested embedding dimension, then GAP.
        self.proj = nn.Sequential(
            nn.Conv2d(c_prev, embedding_dim, kernel_size=1, bias=False),
            norm(embedding_dim),
            nn.ReLU(inplace=True),
        )
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = self.proj(x)
        x = self.avgpool(x)
        return torch.flatten(x, 1)


class AntiCheatCNN(nn.Module):
    """An encoder designed *not* to be able to reconstruct the update rule.

    Motivated by SELF_CRITICISM.md (v2 roadmap #1) and the prior supervised
    paper's two anti-cheating principles:

    1. **The first-layer kernel must not span a "T-tetromino"** — a full 3-cell
       neighbourhood together with the output cell it produces. A ``2x2`` kernel
       sees only two of the three input cells at once, so the first layer
       *cannot* directly read a rule-table entry. Deeper layers use ``2x2``
       kernels on pooled features (which no longer correspond to raw cells), so
       the receptive field still grows to capture mesoscopic structure.
    2. **The representation handed to the projector must be a small bottleneck**
       (default 64-d), too small to comfortably encode the 8-bit rule.

    The final activation is intentionally dropped, so embeddings are *signed*
    (not clamped to the non-negative orthant) — this keeps the full angular
    range for the cosine-metric clustering used downstream.
    """

    def __init__(
        self,
        embedding_dim: int = 64,
        channels: tuple[int, ...] = (16, 32, 64, 64),
        norm_layer: str = "group",
        num_groups: int = 8,
        in_channels: int = 1,
    ) -> None:
        super().__init__()
        self.embedding_dim = embedding_dim
        norm = make_norm_layer(norm_layer, num_groups)

        def block(c_in: int, c_out: int) -> nn.Sequential:
            # 2x2 kernel, no padding -> cannot envelope a 3-cell neighbourhood.
            return nn.Sequential(
                nn.Conv2d(c_in, c_out, kernel_size=2, stride=1, padding=0, bias=False),
                norm(c_out),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(2),
            )

        c_prev = in_channels
        stages = []
        for c in channels:
            stages.append(block(c_prev, c))
            c_prev = c
        self.features = nn.Sequential(*stages)
        # 1x1 projection to the small bottleneck, then GAP. No final ReLU, so the
        # embedding can take negative values.
        self.bottleneck = nn.Sequential(
            nn.Conv2d(c_prev, embedding_dim, kernel_size=1, bias=False),
            norm(embedding_dim),
        )
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = self.bottleneck(x)
        x = self.avgpool(x)
        return torch.flatten(x, 1)
