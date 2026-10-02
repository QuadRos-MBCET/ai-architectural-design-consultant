import os
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from models.diffusion.floorplan_ddpm import ConditionalDDPM

def train_diffusion(data_path: str = "data/processed/floorplans_dataset.pt", epochs: int = 50, batch_size: int = 32, lr: float = 1e-3):
    if not os.path.exists(data_path):
        print(f"Error: Processed dataset not found at {data_path}.")
        return

    checkpoint_dir = os.path.join(os.path.dirname(__file__), "checkpoints")
    os.makedirs(checkpoint_dir, exist_ok=True)

    print(f"Loading floorplan dataset from {data_path} for DDPM Diffusion Model training...")
    dataset_dict = torch.load(data_path)
    layouts = dataset_dict["layouts"]
    conditions = dataset_dict["conditions"]

    dataset = TensorDataset(layouts, conditions)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model = ConditionalDDPM(
        max_rooms=layouts.size(1),
        feature_dim=layouts.size(-1),
        cond_dim=conditions.size(-1),
        timesteps=100
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    print(f"Starting Conditional DDPM Diffusion Training for {epochs} epochs on {device}...")

    for epoch in range(1, epochs + 1):
        model.train()
        total_epoch_loss = 0.0
        
        for batch_layouts, batch_conds in loader:
            batch_layouts = batch_layouts.to(device)
            batch_conds = batch_conds.to(device)
            batch_size = batch_layouts.size(0)

            # Sample random timesteps t for each sample in batch
            t = torch.randint(0, model.timesteps, (batch_size,), device=device).long()

            # Forward diffusion: add noise to x_0
            noisy_layouts, target_noise = model.q_sample(batch_layouts, t)

            # Predict added noise
            predicted_noise = model(noisy_layouts, t, batch_conds)

            loss = criterion(predicted_noise, target_noise)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_epoch_loss += loss.item()
            
        avg_loss = total_epoch_loss / len(loader)
        if epoch % 10 == 0 or epoch == 1 or epoch == epochs:
            print(f"Epoch [{epoch}/{epochs}] - DDPM Noise MSE Loss: {avg_loss:.4f}")

    ckpt_path = os.path.join(checkpoint_dir, "ddpm_latest.pt")
    torch.save({
        "epoch": epochs,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "loss": avg_loss,
        "max_rooms": layouts.size(1),
        "feature_dim": layouts.size(-1),
        "cond_dim": conditions.size(-1),
        "timesteps": 100
    }, ckpt_path)
    print(f"Successfully saved DDPM Diffusion checkpoint to {ckpt_path}")

if __name__ == "__main__":
    train_diffusion()
