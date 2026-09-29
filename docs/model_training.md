# Model Training & Inference Guide

This guide covers dataset preparation, model architecture configurations, training execution, and inference procedures for the **Conditional VAE** and **Conditional GAN** floor-plan generators.

---

## 1. Dataset Preprocessing Pipeline

Run the preprocessing script to build layout tensors:

```bash
python -m preprocessing.dataset_builder
```

This populates `data/processed/floorplans_dataset.pt` with encoded layout matrices $(N_{\text{samples}}, 16, 26)$ and condition vectors $(N_{\text{samples}}, 24)$.

---

## 2. Training PyTorch Conditional VAE

To train the Variational Autoencoder:

```bash
python -m models.vae.train
```

### Hyperparameters
- **Epochs**: `50`
- **Batch Size**: `32`
- **Learning Rate**: `1e-3`
- **Latent Dimension**: `64`
- **Loss Weighting**: $L_{\text{MSE\_coords}} + 2.0 \cdot L_{\text{MSE\_types}} + 0.01 \cdot L_{\text{KLD}}$
- **Checkpoint Location**: `models/vae/checkpoints/vae_latest.pt`

---

## 3. Training PyTorch Conditional GAN

To train the Conditional Generative Adversarial Network:

```bash
python -m models.gan.train
```

### Hyperparameters
- **Epochs**: `50`
- **Batch Size**: `32`
- **Learning Rate**: `2e-4` (Adam optimizer with $\beta_1 = 0.5$)
- **Noise Vector Dimension**: `64`
- **Loss**: Binary Cross Entropy (BCE)
- **Checkpoint Location**: `models/gan/checkpoints/cgan_latest.pt`

---

## 4. Model Inference & Evaluation

Inference runs automatically via the FastAPI endpoint `POST /api/floorplan/generate` or programmatically:

```python
from models.gan.inference import generate_with_gan

reqs = {"building_type": "library", "building_width": 30.0, "building_length": 20.0}
floorplan_json, is_trained, status = generate_with_gan(reqs)
```
