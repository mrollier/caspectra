"""Training loop for the invariant regressor — Lever A (FOUNDATIONS.md §4).

Mirrors :class:`caspectra.train.trainer.Trainer`'s conventions (plain loop,
periodic checkpoints, CSV log + PNG curve, no frameworks) for the supervised
regression task: predict per-rule damage-spreading invariants from single
diagrams.

Two design points with scientific content:

* **Standardization is fitted on train-split rules only** (leakage guard —
  held-out rules must not influence the target scaling). The scaler is stored
  in every checkpoint so evaluation can invert it.
* **Validation is the criterion-6 preview**: each epoch, per-feature R² over
  the *held-out rules'* diagrams. R² is invariant under the (shared) affine
  standardization, so values are comparable to the raw-target scale. This
  curve is a *preview only* — it is scored on the test panel and must never
  drive any training decision.
* **Checkpoint selection (rev 13, M9) uses a separate inner fold** carved from
  the *training* rules' diagrams. The rev-10 protocol kept final-epoch weights,
  which under heavy degradation augmentation samples an oscillating validation
  curve at an arbitrary point; the fourth referee report (§3.17) is right that
  reporting the resulting run-to-run spread as an estimator-family property
  confounds the estimator with the selection rule. Selecting on the held-out
  rules would be selection on the test set, so the inner fold holds out
  training-rule *diagrams* instead: every training rule stays in the training
  set, and the only variable that changes relative to rev 10 is which epoch's
  weights are kept.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless; we only save PNGs
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402
from torch.utils.data import DataLoader  # noqa: E402

from caspectra.config import TrainConfig  # noqa: E402
from caspectra.degradation import degrade_batch  # noqa: E402
from caspectra.utils import ensure_dir  # noqa: E402

__all__ = ["RegressionTrainer", "r2_per_feature"]


def r2_per_feature(predictions: np.ndarray, targets: np.ndarray) -> np.ndarray:
    """Per-column coefficient of determination R² (1 − SS_res / SS_tot).

    ``nan`` when a target column is constant (SS_tot = 0) — that happens for
    degenerate rule subsets (e.g. all-ordered smoke sets) and must not crash.
    """
    residual = np.sum((targets - predictions) ** 2, axis=0)
    total = np.sum((targets - targets.mean(axis=0)) ** 2, axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        r2 = 1.0 - residual / total
    # Constant columns: exact-zero SS_tot, but also the float-epsilon residue of
    # averaging identical values (~1e-33), which would otherwise produce R² ~ -1e30.
    degenerate = total <= len(targets) * (1e-9 * np.maximum(1.0, np.abs(targets).max(axis=0))) ** 2
    r2[degenerate] = np.nan
    return r2


class RegressionTrainer:
    """Train an :class:`~caspectra.models.regressor.InvariantRegressor`.

    Parameters
    ----------
    model, train_loader, val_loader, optimizer, device, config:
        Standard components; loaders yield ``(image, metadata)`` batches where
        ``metadata["equiv_class_rep"]`` keys the target lookup.
    targets_by_rule:
        Raw (unstandardized) target vector per rule for *all* rules.
    train_rules, holdout_rules:
        The leave-rules-out split; the scaler is fitted on ``train_rules`` only.
    target_names:
        Feature names, used for the CSV header and reports.
    """

    def __init__(
        self,
        model: torch.nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        optimizer: torch.optim.Optimizer,
        device: torch.device,
        config: TrainConfig,
        *,
        targets_by_rule: dict[int, np.ndarray],
        train_rules: list[int],
        holdout_rules: list[int],
        target_names: list[str],
        select_loader: DataLoader | None = None,
    ) -> None:
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.select_loader = select_loader
        self.optimizer = optimizer
        self.device = device
        self.config = config
        self.output_dir = ensure_dir(config.output_dir)
        self.train_rules = list(train_rules)
        self.holdout_rules = list(holdout_rules)
        self.target_names = list(target_names)

        # Standardize on the train split only (leakage guard).
        train_matrix = np.stack([targets_by_rule[r] for r in self.train_rules])
        self.scaler_mean = train_matrix.mean(axis=0)
        self.scaler_std = np.maximum(train_matrix.std(axis=0), 1e-8)
        self._target_lookup = {
            int(rule): torch.tensor((vec - self.scaler_mean) / self.scaler_std, dtype=torch.float32)
            for rule, vec in targets_by_rule.items()
        }

        # Rev-10 C-i: dedicated stream so the degradation draw is reproducible
        # given the (globally seeded) batch order; validation stays clean.
        self._degrade_rng = (
            np.random.default_rng(np.random.SeedSequence([20260705]))
            if config.degradation_augment
            else None
        )

        self.history: list[float] = []
        self.val_r2_history: list[np.ndarray] = []
        # Rev-13 M9: inner-fold selection state. ``None`` reproduces the
        # rev-10 final-epoch protocol exactly.
        self.select_loss_history: list[float] = []
        self.best_select_loss: float = math.inf
        self.best_select_epoch: int = 0

    def _batch_targets(self, metadata: dict) -> torch.Tensor:
        reps = metadata["equiv_class_rep"]
        return torch.stack([self._target_lookup[int(r)] for r in reps]).to(self.device)

    def _train_one_epoch(self) -> float:
        self.model.train()
        running, n_batches = 0.0, 0
        for image, metadata in self.train_loader:
            if self._degrade_rng is not None:
                image = degrade_batch(image, self._degrade_rng)
            predictions = self.model(image.to(self.device))
            loss = torch.nn.functional.mse_loss(predictions, self._batch_targets(metadata))
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            running += loss.item()
            n_batches += 1
        return running / max(1, n_batches)

    @torch.no_grad()
    def _validate(self) -> np.ndarray:
        """Per-feature R² over the held-out rules' diagrams (criterion-6 preview)."""
        self.model.eval()
        preds, targets = [], []
        for image, metadata in self.val_loader:
            preds.append(self.model(image.to(self.device)).cpu().numpy())
            targets.append(self._batch_targets(metadata).cpu().numpy())
        self.model.train()
        return r2_per_feature(np.concatenate(preds), np.concatenate(targets))

    @torch.no_grad()
    def _selection_loss(self) -> float:
        """Mean MSE on the inner fold: unseen *diagrams* of *training* rules.

        Clean (never degraded), matching evaluation-time input, and disjoint
        from both the training diagrams and the held-out rule panel.
        """
        self.model.eval()
        total, n = 0.0, 0
        for image, metadata in self.select_loader:
            predictions = self.model(image.to(self.device))
            loss = torch.nn.functional.mse_loss(
                predictions, self._batch_targets(metadata), reduction="sum"
            )
            total += float(loss.item())
            n += predictions.numel()
        self.model.train()
        return total / max(1, n)

    def train(self) -> list[float]:
        """Run the full loop; return the per-epoch train-loss history."""
        csv_path = self.output_dir / "loss_log.csv"
        with csv_path.open("w", newline="") as f:
            writer = csv.writer(f)
            header = (
                ["epoch", "train_loss"]
                + [f"val_r2_{n}" for n in self.target_names]
                + ["val_r2_median"]
            )
            if self.select_loader is not None:
                header.append("select_loss")
            writer.writerow(header)
            for epoch in range(1, self.config.epochs + 1):
                epoch_loss = self._train_one_epoch()
                val_r2 = self._validate()
                self.history.append(epoch_loss)
                self.val_r2_history.append(val_r2)
                median = float(np.nanmedian(val_r2)) if not np.all(np.isnan(val_r2)) else math.nan
                row = [epoch, epoch_loss, *val_r2.tolist(), median]
                if self.select_loader is not None:
                    select_loss = self._selection_loss()
                    self.select_loss_history.append(select_loss)
                    row.append(select_loss)
                    if select_loss < self.best_select_loss:
                        self.best_select_loss = select_loss
                        self.best_select_epoch = epoch
                        self.save_checkpoint(self.output_dir / "checkpoint_selected.pt", epoch)
                writer.writerow(row)
                f.flush()
                if epoch % self.config.checkpoint_every == 0:
                    self.save_checkpoint(self.output_dir / f"checkpoint_epoch{epoch}.pt", epoch)

        # Final-epoch weights are always kept, so the rev-10/rev-11 numbers stay
        # reproducible from a selected-checkpoint run directory.
        self.save_checkpoint(self.output_dir / "checkpoint_final.pt", self.config.epochs)
        if self.select_loader is not None:
            print(
                f"[lever-a] selected epoch {self.best_select_epoch}/{self.config.epochs} "
                f"(inner-fold MSE {self.best_select_loss:.5f}; "
                f"final-epoch {self.select_loss_history[-1]:.5f})"
            )
        self._plot(self.output_dir / "loss_curve.png")
        return self.history

    def save_checkpoint(self, path: str | Path, epoch: int) -> None:
        """Save model/optimizer state plus everything evaluation needs."""
        torch.save(
            {
                "model_state": self.model.state_dict(),
                "optimizer_state": self.optimizer.state_dict(),
                "epoch": epoch,
                "history": self.history,
                "scaler_mean": self.scaler_mean,
                "scaler_std": self.scaler_std,
                "train_rules": self.train_rules,
                "holdout_rules": self.holdout_rules,
                "target_names": self.target_names,
                "selection": {
                    "enabled": self.select_loader is not None,
                    "best_epoch": self.best_select_epoch,
                    "best_inner_fold_mse": self.best_select_loss,
                },
            },
            path,
        )

    def _plot(self, path: str | Path) -> None:
        epochs = range(1, len(self.history) + 1)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(epochs, self.history, marker="o", ms=3, color="C0", label="train MSE")
        ax.set_xlabel("epoch")
        ax.set_ylabel("train MSE (standardized targets)", color="C0")
        ax.set_title("Invariant regression: loss + held-out-rule R²")
        ax2 = ax.twinx()
        medians = [
            float(np.nanmedian(r)) if not np.all(np.isnan(r)) else math.nan
            for r in self.val_r2_history
        ]
        ax2.plot(epochs, medians, marker="s", ms=3, color="C1", label="val R² (median)")
        ax2.set_ylabel("held-out-rule R² (criterion 6 preview)", color="C1")
        ax2.axhline(0.5, color="C1", lw=0.8, ls="--", alpha=0.6)  # criterion-6 success bar
        fig.tight_layout()
        fig.savefig(path, dpi=120)
        plt.close(fig)
