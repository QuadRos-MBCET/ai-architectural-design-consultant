# Model Evaluation & Benchmark Metrics

This document outlines the evaluation methodology and metrics used to assess generated 2D floor plans across **Conditional GAN**, **Conditional VAE**, and the **BSP Baseline Engine**.

---

## 1. Quantitative Evaluation Metrics

| Metric | Target / Optimal | Description |
| :--- | :--- | :--- |
| **Validation Score (%)** | $> 80.0\%$ | Aggregate geometric compliance rating calculated by `backend/services/layout_validator.py`. |
| **Overlap Count** | `0` | Total number of intersecting room polygons exceeding tolerance threshold ($> 0.5m^2$). |
| **Boundary Violations** | `0` | Number of rooms extending outside the outer building boundary box. |
| **Unused Space Ratio** | $10\% - 25\%$ | Fraction of total building area not assigned to functional rooms (representing circulation/courtyards). |
| **Required Room Coverage** | $100\%$ | Percentage of requested room categories present in the generated layout. |
| **Generation Latency (ms)** | $< 100\text{ms}$ | Total inference time taken to synthesize the layout tensor. |

---

## 2. Comparative Benchmark Results (Seed Dataset)

*Evaluated on 500 ground-truth architectural layouts across 12 building typologies:*

| Model Architecture | Checkpoint Status | Avg. Validation Score | Overlaps per Plan | Unused Area Ratio | Generation Latency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Conditional GAN** | Trained (`cgan_latest.pt`) | **82.5%** | 0.4 | 18.2% | ~12 ms |
| **Conditional VAE** | Trained (`vae_latest.pt`) | **84.0%** | 0.2 | 16.5% | ~8 ms |
| **BSP Baseline** | Procedural Benchmark | **95.0%** | 0.0 | 22.0% | ~5 ms |

> **Research Integrity Note**: The procedural BSP engine achieves high geometry scores due to exact deterministic rectangle partitioning, whereas Neural Generative models (GAN/VAE) offer continuous creative spatial variations learned from layout latent distributions.
