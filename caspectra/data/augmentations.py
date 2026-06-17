"""Augmentations for self-supervised training on CA spacetime diagrams.

This is the scientifically load-bearing part of the project (BUILD_BRIEF.md
§3.3). The central constraint is that the encoder must learn *mesoscopic
behaviour* (phenotype), not the local update rule (genotype). The choice of
positive-pair augmentations is what enforces that:

* **CyclicShift** is an exact symmetry under periodic boundary conditions — it
  moves information without destroying it, telling the model "absolute spatial
  phase is irrelevant".
* **CoarseGrain** deliberately destroys microscopic / rule-level detail while
  preserving mesoscopic structure. This is the key invariance for
  genotype-suppression: two views that disagree on fine detail but agree on
  coarse structure force the encoder to represent the latter.

Each augmentation is a small callable class operating on a ``(1, H, W)`` float
tensor with values in ``[0, 1]``. Toggleable augmentations default to OFF and
are documented as experimental conditions.

Intentionally excluded as positive-pair augmentations (see BUILD_BRIEF.md §3.3):

* **Vertical / time flips** — time is not reversible for a CA; a time-reversed
  diagram is not a valid evolution.
* **90-degree rotations / transposes** — these mix the space and time axes,
  which are physically distinct.
* **Salt-and-pepper noise** — empirically hurt without helping.

These are not implemented and are not registered in any stack.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol

import torch
import torch.nn.functional as F

__all__ = [
    "Augmentation",
    "CyclicShift",
    "CoarseGrain",
    "HorizontalFlip",
    "Invert",
    "RandomResizedCropConservative",
    "AugmentationStack",
    "AugmentationConfig",
    "build_augmentation_stack",
    "default_augmentation_stack",
    "TwoViewTransform",
]


class Augmentation(Protocol):
    """A callable mapping a ``(1, H, W)`` tensor to a ``(1, H, W)`` tensor."""

    def __call__(self, x: torch.Tensor) -> torch.Tensor: ...


# ---------------------------------------------------------------------------
# Primary (default-on) augmentations
# ---------------------------------------------------------------------------


class CyclicShift:
    """Roll the image along the horizontal (space) axis by a random offset.

    Exact symmetry under periodic boundary conditions: no information is lost,
    only the absolute spatial phase changes. Primary, default-on augmentation.
    """

    def __init__(self, generator: torch.Generator | None = None) -> None:
        self.generator = generator

    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        width = x.shape[-1]
        offset = int(torch.randint(0, width, (1,), generator=self.generator).item())
        return torch.roll(x, shifts=offset, dims=-1)


class CoarseGrain:
    """Average-pool by ``kernel`` then upsample back to the original size.

    The shape is preserved but each ``kernel x kernel`` block becomes a single
    averaged (multi-level) value, destroying microscopic / rule-level detail
    while keeping mesoscopic structure. Primary, default-on augmentation — this
    is the key invariance for genotype-suppression.

    Applied stochastically with probability ``p`` (SELF_CRITICISM.md v2 roadmap
    #4): when ``p < 1`` some training views keep full fine detail, so the encoder
    is not trained *exclusively* on blurred inputs while evaluation feeds raw
    diagrams (the train/eval distribution mismatch). ``p=1`` reproduces the old
    always-on behaviour.
    """

    def __init__(
        self,
        kernel: int = 2,
        mode: str = "nearest",
        p: float = 1.0,
        generator: torch.Generator | None = None,
    ) -> None:
        self.kernel = kernel
        self.mode = mode
        self.p = p
        self.generator = generator

    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        if self.p < 1.0 and torch.rand(1, generator=self.generator).item() >= self.p:
            return x
        _, h, w = x.shape
        pooled = F.avg_pool2d(x.unsqueeze(0), kernel_size=self.kernel)
        # Upsample to the exact original size (robust to non-divisible dims).
        upsampled = F.interpolate(pooled, size=(h, w), mode=self.mode)
        return upsampled.squeeze(0)


# ---------------------------------------------------------------------------
# Toggleable (default-off, experimental) augmentations
# ---------------------------------------------------------------------------


class HorizontalFlip:
    """Mirror left-right with probability ``p``.

    Toggleable, OFF by default. This is an *equivalence-class* operation: it
    maps a rule's diagram toward its reflection partner, so enabling it tests a
    specific experimental condition rather than a generic invariance.
    """

    def __init__(self, p: float = 0.5, generator: torch.Generator | None = None) -> None:
        self.p = p
        self.generator = generator

    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        if torch.rand(1, generator=self.generator).item() < self.p:
            return torch.flip(x, dims=[-1])
        return x


class Invert:
    """Map ``x -> 1 - x`` with probability ``p``.

    Toggleable, OFF by default. Like :class:`HorizontalFlip` this is an
    equivalence map (0<->1 complementation), so it is an experimental condition.
    """

    def __init__(self, p: float = 0.5, generator: torch.Generator | None = None) -> None:
        self.p = p
        self.generator = generator

    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        if torch.rand(1, generator=self.generator).item() < self.p:
            return 1.0 - x
        return x


class RandomResizedCropConservative:
    """Random square crop (area in ``scale``) resized back to the original size.

    OFF by default. Note: unlike natural images, a crop of a CA diagram still
    contains the full rule table, so it does **not** suppress genotype. Only a
    conservative scale range is used so the mesoscopic structure stays visible.
    """

    def __init__(
        self,
        scale: tuple[float, float] = (0.6, 1.0),
        generator: torch.Generator | None = None,
    ) -> None:
        self.scale = scale
        self.generator = generator

    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        _, h, w = x.shape
        area = h * w
        factor = (
            self.scale[0]
            + (self.scale[1] - self.scale[0]) * torch.rand(1, generator=self.generator).item()
        )
        side = int(round(math.sqrt(factor * area)))
        crop_h = min(side, h)
        crop_w = min(side, w)
        top = int(torch.randint(0, h - crop_h + 1, (1,), generator=self.generator).item())
        left = int(torch.randint(0, w - crop_w + 1, (1,), generator=self.generator).item())
        crop = x[:, top : top + crop_h, left : left + crop_w]
        resized = F.interpolate(
            crop.unsqueeze(0), size=(h, w), mode="bilinear", align_corners=False
        )
        return resized.squeeze(0)


# Intentionally excluded — see BUILD_BRIEF.md §3.3. Left as named stubs so the
# omission is explicit and discoverable, and never registered in a stack:
#   class TimeFlip(...)            # intentionally excluded — time is irreversible
#   class Transpose(...)          # intentionally excluded — mixes space/time axes
#   class SaltAndPepperNoise(...) # intentionally excluded — hurt without helping


# ---------------------------------------------------------------------------
# Stack + configuration
# ---------------------------------------------------------------------------


class AugmentationStack:
    """Apply a list of augmentations in sequence to a single image."""

    def __init__(self, transforms: list[Augmentation]) -> None:
        self.transforms = transforms

    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        for transform in self.transforms:
            x = transform(x)
        return x


@dataclass
class AugmentationConfig:
    """Which augmentations are enabled and how views are paired.

    Defaults match BUILD_BRIEF.md §3.3: cyclic-shift + coarse-grain ON; flip,
    invert and crop OFF (experimental).
    """

    cyclic_shift: bool = True
    coarse_grain: bool = True
    horizontal_flip: bool = False
    invert: bool = False
    random_resized_crop: bool = False
    coarse_grain_kernel: int = 2
    coarse_grain_prob: float = 0.5  # stochastic: some views keep fine detail
    crop_scale: tuple[float, float] = (0.6, 1.0)
    flip_prob: float = 0.5
    invert_prob: float = 0.5
    # "symmetric": both views drawn from the same stochastic stack (default).
    # "asymmetric_coarse": view A shift-only, view B always coarse-grained.
    mode: str = "symmetric"


def build_augmentation_stack(config: AugmentationConfig) -> AugmentationStack:
    """Build an :class:`AugmentationStack` from a config, in a fixed order."""
    transforms: list[Augmentation] = []
    if config.cyclic_shift:
        transforms.append(CyclicShift())
    if config.coarse_grain:
        transforms.append(
            CoarseGrain(kernel=config.coarse_grain_kernel, p=config.coarse_grain_prob)
        )
    if config.horizontal_flip:
        transforms.append(HorizontalFlip(p=config.flip_prob))
    if config.invert:
        transforms.append(Invert(p=config.invert_prob))
    if config.random_resized_crop:
        transforms.append(RandomResizedCropConservative(scale=config.crop_scale))
    return AugmentationStack(transforms)


def default_augmentation_stack() -> AugmentationStack:
    """The default stack: cyclic-shift then coarse-grain."""
    return build_augmentation_stack(AugmentationConfig())


class TwoViewTransform:
    """Produce a positive pair (two augmented views) from one image.

    Modes (BUILD_BRIEF.md §3.3):

    * ``symmetric`` (default): both views are drawn independently from the same
      stochastic stack. Standard BYOL/SimSiam setup.
    * ``asymmetric_coarse`` (experimental): view A is lightly augmented
      (shift only); view B is always coarse-grained. Explicitly trains
      invariance to microscopic detail.
    """

    def __init__(self, config: AugmentationConfig | None = None) -> None:
        self.config = config or AugmentationConfig()
        if self.config.mode == "symmetric":
            self._view_a = build_augmentation_stack(self.config)
            self._view_b = build_augmentation_stack(self.config)
        elif self.config.mode == "asymmetric_coarse":
            # View A: shift only. View B: shift + forced coarse-grain.
            self._view_a = AugmentationStack([CyclicShift()])
            self._view_b = AugmentationStack(
                [CyclicShift(), CoarseGrain(kernel=self.config.coarse_grain_kernel)]
            )
        else:
            raise ValueError(
                f"Unknown TwoViewTransform mode: {self.config.mode!r}; "
                "expected 'symmetric' or 'asymmetric_coarse'."
            )

    def __call__(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        return self._view_a(x), self._view_b(x)
