"""Shape tests for dataset items and both encoders (BUILD_BRIEF.md §4)."""

from __future__ import annotations

import pytest
import torch

from caspectra.data.dataset import SpacetimeDataset
from caspectra.models.encoder import AntiCheatCNN, ResNet18Encoder, SmallCNNEncoder


@pytest.mark.parametrize("grid", [64, 128])
def test_dataset_item_shape(tmp_path, grid: int) -> None:
    ds = SpacetimeDataset(
        rules=[90], n_ic_per_rule=1, grid_size=grid, cache_dir=str(tmp_path), seed=0
    )
    image, _ = ds[0]
    assert image.shape == (1, grid, grid)


@pytest.mark.parametrize("grid", [64, 128])
def test_resnet_encoder_output_shape(grid: int) -> None:
    enc = ResNet18Encoder(small_input=(grid <= 64))
    out = enc(torch.randn(2, 1, grid, grid))
    assert out.shape == (2, enc.embedding_dim)
    assert enc.embedding_dim == 512


@pytest.mark.parametrize("grid", [64, 128])
def test_smallcnn_encoder_output_shape(grid: int) -> None:
    enc = SmallCNNEncoder()
    out = enc(torch.randn(2, 1, grid, grid))
    assert out.shape == (2, enc.embedding_dim)


def test_resnet_width_multiplier_halves_embedding_dim() -> None:
    enc = ResNet18Encoder(width_multiplier=0.5)
    assert enc.embedding_dim == 256
    out = enc(torch.randn(2, 1, 128, 128))
    assert out.shape == (2, 256)


@pytest.mark.parametrize("norm", ["group", "batch"])
def test_resnet_supports_both_norm_layers(norm: str) -> None:
    enc = ResNet18Encoder(norm_layer=norm, small_input=True)
    out = enc(torch.randn(2, 1, 64, 64))
    assert out.shape == (2, 512)


def test_smallcnn_param_count_is_modest() -> None:
    """SmallCNN should be a light alternative (~0.5-2M params)."""
    enc = SmallCNNEncoder()
    n_params = sum(p.numel() for p in enc.parameters())
    assert 0.3e6 <= n_params <= 2.5e6


# ---------------------------------------------------------------------------
# AntiCheatCNN (SELF_CRITICISM.md v2 roadmap #1)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("grid", [64, 128])
def test_anticheat_encoder_output_shape(grid: int) -> None:
    enc = AntiCheatCNN(embedding_dim=64)
    out = enc(torch.randn(2, 1, grid, grid))
    assert out.shape == (2, enc.embedding_dim)


def test_anticheat_first_kernel_cannot_span_a_t_tetromino() -> None:
    """The first conv must be 2x2 so it cannot see a full 3-cell neighbourhood
    plus its output cell (a "T-tetromino"); this prevents the first layer from
    learning rule-table detectors (paper principle 1)."""
    enc = AntiCheatCNN(embedding_dim=64)
    first_conv = next(m for m in enc.modules() if isinstance(m, torch.nn.Conv2d))
    assert tuple(first_conv.kernel_size) == (2, 2)
    assert first_conv.in_channels == 1


def test_anticheat_embeddings_are_signed_not_relu_clamped() -> None:
    """Embeddings must not be clamped to the non-negative orthant (the final
    activation is dropped), so cosine-based clustering keeps full angular range."""
    torch.manual_seed(0)
    enc = AntiCheatCNN(embedding_dim=64)
    out = enc(torch.randn(8, 1, 64, 64))
    assert (out < 0).any()


def test_anticheat_small_bottleneck_is_default() -> None:
    """Default embedding dim is a small bottleneck (paper principle 3: the
    pre-head representation should be too small to comfortably encode the rule)."""
    enc = AntiCheatCNN()
    assert enc.embedding_dim <= 64
