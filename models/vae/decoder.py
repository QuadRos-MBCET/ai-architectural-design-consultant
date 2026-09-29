import torch
import torch.nn as nn

class FloorplanVAEDecoder(nn.Module):
    """
    Decoder network for Variational Autoencoder (VAE) reconstructing floor plan layouts.
    """
    def __init__(self, output_dim: int = 26, max_rooms: int = 16, cond_dim: int = 24, latent_dim: int = 64):
        super().__init__()
        self.output_dim = output_dim
        self.max_rooms = max_rooms
        self.flat_dim = max_rooms * output_dim

        self.fc_cond = nn.Sequential(
            nn.Linear(cond_dim, 64),
            nn.ReLU(),
            nn.BatchNorm1d(64)
        )

        self.net = nn.Sequential(
            nn.Linear(latent_dim + 64, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Linear(128, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, self.flat_dim)
        )

    def forward(self, z: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        batch_size = z.size(0)
        cond_feat = self.fc_cond(cond)
        
        h = torch.cat([z, cond_feat], dim=1)
        out_flat = self.net(h)
        
        out = out_flat.view(batch_size, self.max_rooms, self.output_dim)
        
        # Apply Sigmoid activation to normalized coordinates [0, 1]
        coords = torch.sigmoid(out[:, :, 0:4])
        # Apply Softmax to room type logits across class channels
        types = torch.softmax(out[:, :, 4:], dim=-1)
        
        return torch.cat([coords, types], dim=-1)
