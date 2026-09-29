import torch
import torch.nn as nn
from typing import Tuple

class FloorplanVAEEncoder(nn.Module):
    """
    Encoder network for Variational Autoencoder (VAE) operating on floor plan layout tensors.
    """
    def __init__(self, input_dim: int = 26, max_rooms: int = 16, cond_dim: int = 24, latent_dim: int = 64):
        super().__init__()
        self.input_dim = input_dim
        self.max_rooms = max_rooms
        self.flat_dim = max_rooms * input_dim
        
        self.fc_cond = nn.Sequential(
            nn.Linear(cond_dim, 64),
            nn.ReLU(),
            nn.BatchNorm1d(64)
        )
        
        self.net = nn.Sequential(
            nn.Linear(self.flat_dim + 64, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU()
        )
        
        self.fc_mu = nn.Linear(128, latent_dim)
        self.fc_logvar = nn.Linear(128, latent_dim)

    def forward(self, x: torch.Tensor, cond: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        # Flatten layout tensor
        batch_size = x.size(0)
        x_flat = x.view(batch_size, -1)
        cond_feat = self.fc_cond(cond)
        
        h = torch.cat([x_flat, cond_feat], dim=1)
        feat = self.net(h)
        
        mu = self.fc_mu(feat)
        logvar = self.fc_logvar(feat)
        return mu, logvar
