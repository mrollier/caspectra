"""Tests for the eval/ modules (BUILD_BRIEF.md §3.6-3.8)."""

from __future__ import annotations

import numpy as np
import pytest
import torch
from torch.utils.data import DataLoader

from caspectra.data.dataset import SpacetimeDataset
from caspectra.eval.cluster import (
    cluster_count_stability,
    cluster_metrics,
    cluster_pipeline,
    contingency_table,
    genotype_phenotype_diagnostic,
    l2_normalize,
    purity,
)
from caspectra.eval.embed import extract_embeddings
from caspectra.eval.labels import RuleLabels, load_rule_labels
from caspectra.eval.probes import run_probes
from caspectra.eval.visualize import save_per_cluster_samples, scatter_three_panel
from caspectra.models.byol import SimSiam
from caspectra.models.encoder import SmallCNNEncoder

# ---------------------------------------------------------------------------
# Embedding extraction
# ---------------------------------------------------------------------------


def test_extract_embeddings_shapes(tmp_path) -> None:
    ds = SpacetimeDataset(
        rules=[90, 110], n_ic_per_rule=4, grid_size=32, cache_dir=str(tmp_path), seed=0
    )
    loader = DataLoader(ds, batch_size=4)
    model = SimSiam(SmallCNNEncoder(embedding_dim=32))
    emb, rules, reps = extract_embeddings(model, loader, torch.device("cpu"))
    assert emb.shape == (8, 32)
    assert rules.shape == (8,)
    assert reps.shape == (8,)
    assert set(rules.tolist()) == {90, 110}


# ---------------------------------------------------------------------------
# Label loading
# ---------------------------------------------------------------------------


def test_load_rule_labels_parses_csv(tmp_path) -> None:
    p = tmp_path / "rule_labels.csv"
    p.write_text("rule,lp_class,wolfram_class\n0,1,1\n90,4,3\n110,4,4\n")
    labels = load_rule_labels(str(p))
    assert labels is not None
    assert labels.lp[90] == 4
    assert labels.wolfram[110] == 4
    np.testing.assert_array_equal(labels.lp_array([0, 90, 110]), [1, 4, 4])


def test_load_rule_labels_missing_returns_none(tmp_path) -> None:
    assert load_rule_labels(str(tmp_path / "nope.csv")) is None


# ---------------------------------------------------------------------------
# Linear probes
# ---------------------------------------------------------------------------


def _separable_embeddings(n_per_class: int = 40, n_classes: int = 4, seed: int = 0):
    """One-hot-ish embeddings that are linearly separable by class."""
    rng = np.random.default_rng(seed)
    rules_list = [10, 20, 30, 40][:n_classes]
    embs, rules = [], []
    for idx, rule in enumerate(rules_list):
        centre = np.zeros(n_classes)
        centre[idx] = 5.0
        embs.append(centre + rng.normal(scale=0.3, size=(n_per_class, n_classes)))
        rules.extend([rule] * n_per_class)
    return np.concatenate(embs), np.array(rules)


def test_rule_probe_high_on_separable_data() -> None:
    emb, rules = _separable_embeddings()
    report = run_probes(emb, rules, labels=None, seed=0)
    assert report.rule.accuracy > 0.9
    assert report.rule.n_classes == 4
    assert report.lp is None  # no labels supplied


def test_rule_probe_near_baseline_on_random_data() -> None:
    rng = np.random.default_rng(1)
    rules = np.repeat([10, 20, 30, 40], 40)
    emb = rng.normal(size=(160, 8))  # independent of rule
    report = run_probes(emb, rules, labels=None, seed=0)
    # Cannot beat chance much when features carry no rule information.
    assert report.rule.accuracy < 0.45
    assert report.rule.baseline <= 0.30 + 1e-6


def test_probe_report_summary_and_csv(tmp_path) -> None:
    emb, rules = _separable_embeddings()
    report = run_probes(emb, rules, labels=None, seed=0)
    text = report.summary()
    assert "rule" in text.lower()
    csv_path = tmp_path / "probes.csv"
    report.to_csv(csv_path)
    assert csv_path.exists()


def test_probe_has_balanced_accuracy_and_macro_f1() -> None:
    emb, rules = _separable_embeddings()
    report = run_probes(emb, rules, labels=None, seed=0)
    assert 0.0 <= report.rule.balanced_accuracy <= 1.0
    assert 0.0 <= report.rule.macro_f1 <= 1.0


def test_probe_gap_is_class_minus_rule_accuracy() -> None:
    """The paper's success signal: behaviour-class accuracy minus exact-rule
    accuracy (want large and positive)."""
    emb, rules = _separable_embeddings()
    labels = RuleLabels(lp={10: 0, 20: 0, 30: 1, 40: 1}, wolfram={})
    report = run_probes(emb, rules, labels, seed=0)
    assert report.lp is not None
    assert report.gap == pytest.approx(report.lp.accuracy - report.rule.accuracy)


def test_probe_gap_is_none_without_labels() -> None:
    emb, rules = _separable_embeddings()
    assert run_probes(emb, rules, labels=None, seed=0).gap is None


def test_leave_rules_out_probe_split_transfers_to_unseen_rules() -> None:
    """LP/Wolfram probes can hold out *entire rules* to test transfer to unseen
    rules within a class (SELF_CRITICISM.md v2 roadmap #6). When the embedding
    encodes the LP class (not the rule), it transfers to held-out rules."""
    rng = np.random.default_rng(0)
    rule_to_lp = {10: 0, 11: 0, 12: 0, 13: 0, 20: 1, 21: 1, 22: 1, 23: 1}
    embs, rules = [], []
    for rule, lp in rule_to_lp.items():
        centre = np.zeros(2)
        centre[lp] = 5.0
        embs.append(centre + rng.normal(scale=0.3, size=(20, 2)))
        rules += [rule] * 20
    emb = np.concatenate(embs)
    labels = RuleLabels(lp=rule_to_lp, wolfram={})
    report = run_probes(emb, np.array(rules), labels, seed=0, lp_split="rules")
    assert report.lp is not None
    assert report.lp.accuracy > 0.8  # LP-encoding transfers to unseen rules


# ---------------------------------------------------------------------------
# Clustering primitives
# ---------------------------------------------------------------------------


def test_l2_normalize_gives_unit_rows() -> None:
    X = np.array([[3.0, 4.0], [1.0, 0.0]])
    norm = l2_normalize(X)
    np.testing.assert_allclose(np.linalg.norm(norm, axis=1), [1.0, 1.0])


def test_purity_is_one_for_perfect_clustering() -> None:
    clusters = np.array([0, 0, 1, 1, 2, 2])
    classes = np.array([5, 5, 7, 7, 9, 9])
    assert purity(clusters, classes) == 1.0


def test_purity_below_one_for_mixed_clusters() -> None:
    clusters = np.array([0, 0, 0, 0])
    classes = np.array([1, 1, 2, 2])
    assert purity(clusters, classes) == 0.5


def test_contingency_table_shape() -> None:
    clusters = np.array([0, 0, 1, 1])
    classes = np.array([5, 6, 5, 6])
    table, crows, ccols = contingency_table(clusters, classes)
    assert table.shape == (len(crows), len(ccols))
    assert table.sum() == 4


def test_cluster_metrics_perfect_match() -> None:
    clusters = np.array([0, 0, 1, 1, 2, 2])
    classes = np.array([1, 1, 2, 2, 3, 3])
    m = cluster_metrics(clusters, classes)
    assert m["ari"] == 1.0
    assert m["nmi"] == 1.0
    assert m["purity"] == 1.0


def test_excess_rule_info_is_zero_when_clusters_track_behaviour() -> None:
    """The corrected diagnostic: excess rule info = MI(cluster;rule|LP) =
    MI(cluster;rule) - MI(cluster;LP). When clusters equal the (coarse) LP class,
    they carry NO rule information beyond LP, so excess ~ 0 (phenotype, good)."""
    rules = np.array([1, 1, 2, 2, 3, 3, 4, 4])
    lp = np.array([0, 0, 0, 0, 1, 1, 1, 1])  # LP = deterministic function of rule
    clusters = lp.copy()  # clusters track behaviour (LP), not the exact rule
    diag = genotype_phenotype_diagnostic(clusters, rules, lp)
    assert diag["mi_rule_given_lp"] == pytest.approx(0.0, abs=1e-9)


def test_excess_rule_info_is_positive_when_clusters_track_the_rule() -> None:
    """When clusters resolve the exact rule (finer than LP), they leak genotype:
    excess rule info is strictly positive (the failure mode)."""
    rules = np.array([1, 1, 2, 2, 3, 3, 4, 4])
    lp = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    clusters = rules.copy()
    diag = genotype_phenotype_diagnostic(clusters, rules, lp)
    assert diag["mi_rule_given_lp"] > 0.0


def test_excess_rule_info_is_never_negative() -> None:
    """By the data-processing inequality MI(cluster;rule) >= MI(cluster;LP), so
    the excess is non-negative for any clustering."""
    rng = np.random.default_rng(0)
    rules = rng.integers(0, 8, size=200)
    lp = rules % 3  # LP is a function of rule
    clusters = rng.integers(0, 5, size=200)  # arbitrary clustering
    diag = genotype_phenotype_diagnostic(clusters, rules, lp)
    assert diag["mi_rule_given_lp"] >= -1e-9


def test_cluster_pipeline_recovers_separated_blobs() -> None:
    rng = np.random.default_rng(0)
    centres = np.array([[5, 5, 0], [-5, -5, 0], [5, -5, 0]], dtype=float)
    true = np.repeat([0, 1, 2], 30)
    X = np.concatenate([c + rng.normal(scale=0.4, size=(30, 3)) for c in centres])
    report = cluster_pipeline(X, umap_components=2, min_cluster_size=5, min_samples=3, seed=0)
    assert report.n_clusters >= 2
    assert report.umap_labels.shape == (90,)
    assert report.direct_labels.shape == (90,)
    # Discovered clustering should correlate with the true blobs.
    assert cluster_metrics(report.umap_labels, true)["ari"] > 0.3


def test_cluster_count_stability_sweeps_min_cluster_size() -> None:
    rng = np.random.default_rng(0)
    centres = np.array([[5, 5, 0], [-5, -5, 0], [5, -5, 0]], dtype=float)
    X = np.concatenate([c + rng.normal(scale=0.4, size=(30, 3)) for c in centres])
    sweep = cluster_count_stability(X, [3, 5, 10], umap_components=2, min_samples=3, seed=0)
    assert [s for s, _ in sweep] == [3, 5, 10]
    assert all(n >= 0 for _, n in sweep)


# ---------------------------------------------------------------------------
# Visualisation (smoke: files are produced)
# ---------------------------------------------------------------------------


def test_scatter_three_panel_writes_png(tmp_path) -> None:
    rng = np.random.default_rng(0)
    coords = rng.normal(size=(60, 2))
    rules = np.repeat([10, 20, 30], 20)
    clusters = np.repeat([0, 1, 2], 20)
    path = tmp_path / "umap.png"
    scatter_three_panel(coords, rules, lp_labels=None, cluster_labels=clusters, path=path)
    assert path.exists()


def test_save_per_cluster_samples_writes_grids(tmp_path) -> None:
    rng = np.random.default_rng(0)
    images = rng.random((30, 1, 16, 16)).astype(np.float32)
    embeddings = rng.normal(size=(30, 4))
    clusters = np.repeat([0, 1, -1], 10)  # two clusters + noise
    paths = save_per_cluster_samples(
        images, clusters, embeddings, out_dir=tmp_path, n_per_cluster=4
    )
    # One grid per non-noise cluster.
    assert len(paths) == 2
    for p in paths:
        assert p.exists()
