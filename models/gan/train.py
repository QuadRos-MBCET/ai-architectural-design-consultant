import os
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from models.gan.cgan import FloorplanCGAN

def train_cgan(data_path: str = "data/processed/floorplans_dataset.pt", epochs: int = 50, batch_size: int = 32, lr: float = 2e-4):
    if not os.path.exists(data_path):
        print(f"Error: Processed dataset not found at {data_path}. Run 'python -m preprocessing.dataset_builder' first.")
        return

    checkpoint_dir = os.path.join(os.path.dirname(__file__), "checkpoints")
    os.makedirs(checkpoint_dir, exist_ok=True)

    print(f"Loading floorplan dataset from {data_path}...")
    dataset_dict = torch.load(data_path)
    layouts = dataset_dict["layouts"]
    conditions = dataset_dict["conditions"]

    dataset = TensorDataset(layouts, conditions)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    cgan = FloorplanCGAN(noise_dim=64, cond_dim=conditions.size(-1), max_rooms=layouts.size(1), feature_dim=layouts.size(-1))
    
    criterion = nn.BCELoss()
    opt_g = torch.optim.Adam(cgan.generator.parameters(), lr=lr, betas=(0.5, 0.999))
    opt_d = torch.optim.Adam(cgan.discriminator.parameters(), lr=lr, betas=(0.5, 0.999))

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cgan.generator.to(device)
    cgan.discriminator.to(device)

    print(f"Starting Conditional GAN Training for {epochs} epochs on {device}...")

    for epoch in range(1, epochs + 1):
        cgan.generator.train()
        cgan.discriminator.train()
        
        loss_d_total, loss_g_total = 0.0, 0.0

        for batch_real, batch_conds in loader:
            b_size = batch_real.size(0)
            batch_real = batch_real.to(device)
            batch_conds = batch_conds.to(device)

            real_labels = torch.ones(b_size, 1, device=device)
            fake_labels = torch.zeros(b_size, 1, device=device)

            # ---------------------
            # Train Discriminator
            # ---------------------
            opt_d.zero_grad()
            out_real = cgan.discriminator(batch_real, batch_conds)
            loss_d_real = criterion(out_real, real_labels)

            z = torch.randn(b_size, cgan.noise_dim, device=device)
            batch_fake = cgan.generator(z, batch_conds)
            out_fake = cgan.discriminator(batch_fake.detach(), batch_conds)
            loss_d_fake = criterion(out_fake, fake_labels)

            loss_d = (loss_d_real + loss_d_fake) / 2.0
            loss_d.backward()
            opt_d.step()
            loss_d_total += loss_d.item()

            # ---------------------
            # Train Generator
            # ---------------------
            opt_g.zero_grad()
            out_fake_g = cgan.discriminator(batch_fake, batch_conds)
            loss_g = criterion(out_fake_g, real_labels)
            loss_g.backward()
            opt_g.step()
            loss_g_total += loss_g.item()

        if epoch % 10 == 0 or epoch == 1 or epoch == epochs:
            avg_d = loss_d_total / len(loader)
            avg_g = loss_g_total / len(loader)
            print(f"Epoch [{epoch}/{epochs}] - Loss D: {avg_d:.4f} | Loss G: {avg_g:.4f}")

    ckpt_path = os.path.join(checkpoint_dir, "cgan_latest.pt")
    torch.save({
        "epoch": epochs,
        "generator_state_dict": cgan.generator.state_dict(),
        "discriminator_state_dict": cgan.discriminator.state_dict(),
        "noise_dim": cgan.noise_dim,
        "cond_dim": conditions.size(-1),
        "max_rooms": layouts.size(1),
        "feature_dim": layouts.size(-1)
    }, ckpt_path)
    print(f"Successfully saved Conditional GAN checkpoint to {ckpt_path}")

if __name__ == "__main__":
    train_cgan()
