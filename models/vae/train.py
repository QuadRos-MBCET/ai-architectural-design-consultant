import os
import torch
from torch.utils.data import TensorDataset, DataLoader
from models.vae.vae import FloorplanVAE

def train_vae(data_path: str = "data/processed/floorplans_dataset.pt", epochs: int = 50, batch_size: int = 32, lr: float = 1e-3):
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

    model = FloorplanVAE(input_dim=layouts.size(-1), max_rooms=layouts.size(1), cond_dim=conditions.size(-1))
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    print(f"Starting VAE Training for {epochs} epochs on {device}...")

    for epoch in range(1, epochs + 1):
        model.train()
        total_epoch_loss = 0.0
        
        for batch_layouts, batch_conds in loader:
            batch_layouts = batch_layouts.to(device)
            batch_conds = batch_conds.to(device)
            
            optimizer.zero_grad()
            recon, mu, logvar = model(batch_layouts, batch_conds)
            loss, c_loss, t_loss, kld = model.loss_function(recon, batch_layouts, mu, logvar)
            
            loss.backward()
            optimizer.step()
            total_epoch_loss += loss.item()
            
        avg_loss = total_epoch_loss / len(loader.dataset)
        if epoch % 10 == 0 or epoch == 1 or epoch == epochs:
            print(f"Epoch [{epoch}/{epochs}] - Loss: {avg_loss:.4f}")

    ckpt_path = os.path.join(checkpoint_dir, "vae_latest.pt")
    torch.save({
        "epoch": epochs,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "loss": avg_loss,
        "input_dim": layouts.size(-1),
        "max_rooms": layouts.size(1),
        "cond_dim": conditions.size(-1)
    }, ckpt_path)
    print(f"Successfully saved VAE checkpoint to {ckpt_path}")

if __name__ == "__main__":
    train_vae()
