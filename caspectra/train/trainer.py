"""Training loop for BYOL / SimSiam (BUILD_BRIEF.md §3.5, §5).

The :class:`Trainer` is intentionally small and framework-free: a plain loop
with EMA momentum scheduling (for BYOL), periodic checkpoints, a CSV loss log
and a matplotlib loss-curve PNG. No Lightning, no W&B (logging is CSV + PNG
only, per the brief).
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless; we only save PNGs
import matplotlib.pyplot as plt  # noqa: E402
import torch  # noqa: E402
from torch.utils.data import DataLoader  # noqa: E402

from caspectra.config import TrainConfig  # noqa: E402
from caspectra.utils import ensure_dir  # noqa: E402

__all__ = ["Trainer", "collapse_std"]


def collapse_std(embeddings: torch.Tensor, eps: float = 1e-8) -> float:
    """Mean per-dimension standard deviation of L2-normalised embeddings.

    A collapse diagnostic (SELF_CRITICISM.md v2 roadmap #3): BYOL/SimSiam minimise
    the loss to its optimum (−1) when the encoder outputs a *constant* vector, so a
    falling loss alone cannot distinguish learning from collapse. This statistic is
    ~0 on collapse and ``~1/sqrt(D)`` for well-spread features; the trainer logs it
    each epoch and the smoke gate asserts it stays above zero.
    """
    z = torch.nn.functional.normalize(embeddings, dim=1, eps=eps)
    return float(z.std(dim=0).mean())


class Trainer:
    """Train an SSL model and log loss, checkpoints and a loss curve.

    The model must expose ``forward(view1, view2) -> scalar_loss``. If it also
    exposes ``update_target(tau)`` (i.e. it is BYOL), the target network is
    EMA-updated each step with ``tau`` cosine-annealed from ``tau_base`` toward
    1.0 over the whole run.

    Parameters
    ----------
    model, dataloader, optimizer, device:
        Standard training components. ``dataloader`` yields
        ``(view1, view2, metadata)`` batches.
    config:
        A :class:`~caspectra.config.TrainConfig` (epochs, checkpoint cadence,
        EMA base momentum, output directory).
    """

    def __init__(
        self,
        model: torch.nn.Module,
        dataloader: DataLoader,
        optimizer: torch.optim.Optimizer,
        device: torch.device,
        config: TrainConfig,
    ) -> None:
        self.model = model.to(device)
        self.dataloader = dataloader
        self.optimizer = optimizer
        self.device = device
        self.config = config
        self.output_dir = ensure_dir(config.output_dir)
        self.history: list[float] = []
        self.std_history: list[float] = []
        self._uses_ema = hasattr(model, "update_target")
        self._total_steps = max(1, config.epochs * len(dataloader))
        self._global_step = 0

    def _tau(self) -> float:
        """Cosine-annealed EMA momentum from ``tau_base`` toward 1.0."""
        base = self.config.tau_base
        progress = self._global_step / self._total_steps
        return 1.0 - (1.0 - base) * (math.cos(math.pi * progress) + 1.0) / 2.0

    def _train_one_epoch(self) -> float:
        self.model.train()
        running, n_batches = 0.0, 0
        for view1, view2, _metadata in self.dataloader:
            view1 = view1.to(self.device)
            view2 = view2.to(self.device)
            loss = self.model(view1, view2)

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            if self._uses_ema:
                self.model.update_target(self._tau())

            running += loss.item()
            n_batches += 1
            self._global_step += 1
        return running / max(1, n_batches)

    @torch.no_grad()
    def _embedding_std(self) -> float:
        """Collapse metric on one batch of online-encoder embeddings."""
        self.model.eval()
        view1, _view2, _metadata = next(iter(self.dataloader))
        std = collapse_std(self.model.extract_embedding(view1.to(self.device)))
        self.model.train()
        return std

    def train(self) -> list[float]:
        """Run the full training loop; return the per-epoch loss history."""
        csv_path = self.output_dir / "loss_log.csv"
        with csv_path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["epoch", "loss", "embedding_std"])
            for epoch in range(1, self.config.epochs + 1):
                epoch_loss = self._train_one_epoch()
                epoch_std = self._embedding_std()
                self.history.append(epoch_loss)
                self.std_history.append(epoch_std)
                writer.writerow([epoch, epoch_loss, epoch_std])
                f.flush()
                if epoch % self.config.checkpoint_every == 0:
                    self.save_checkpoint(self.output_dir / f"checkpoint_epoch{epoch}.pt", epoch)

        self.save_checkpoint(self.output_dir / "checkpoint_final.pt", self.config.epochs)
        self._plot_loss(self.output_dir / "loss_curve.png")
        return self.history

    def save_checkpoint(self, path: str | Path, epoch: int) -> None:
        """Save model + optimizer state and the epoch number."""
        torch.save(
            {
                "model_state": self.model.state_dict(),
                "optimizer_state": self.optimizer.state_dict(),
                "epoch": epoch,
                "history": self.history,
            },
            path,
        )

    def _plot_loss(self, path: str | Path) -> None:
        epochs = range(1, len(self.history) + 1)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(epochs, self.history, marker="o", ms=3, color="C0", label="loss")
        ax.set_xlabel("epoch")
        ax.set_ylabel("loss", color="C0")
        ax.set_title("SSL training loss + collapse metric")
        # Overlay the collapse metric on a twin axis (→ 0 means collapse).
        ax2 = ax.twinx()
        ax2.plot(epochs, self.std_history, marker="s", ms=3, color="C1", label="embedding std")
        ax2.set_ylabel("embedding std (0 = collapse)", color="C1")
        ax2.set_ylim(bottom=0.0)
        fig.tight_layout()
        fig.savefig(path, dpi=120)
        plt.close(fig)
