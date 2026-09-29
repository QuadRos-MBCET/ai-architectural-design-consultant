import torch
import torch.nn as nn

class FloorplanCGANGenerator(nn.Module):
    """
    Generator network for Conditional GAN (CGAN) synthesizing 2D floor plans from noise + prompt conditions.
    """
    def __init__(self, noise_dim: int = 64, cond_dim: int = 24, max_rooms: int = 16, feature_dim: int = 26):
        super().__init__()
        self.max_rooms = max_rooms
        self.feature_dim = feature_dim
        self.flat_dim = max_rooms * feature_dim
        
        self.fc_cond = nn.Sequential(
            nn.Linear(cond_dim, 64),
            nn.ReLU(),
            nn.BatchNorm1d(64)
        )
        
        self.net = nn.Sequential(
            nn.Linear(noise_dim + 64, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Linear(256, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, self.flat_dim)
        )

    def forward(self, z: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        batch_size = z.size(0)
        cond_feat = self.fc_cond(cond)
        h = torch.cat([z, cond_feat], dim=1)
        
        out_flat = self.net(h)
        out = out_flat.view(batch_size, self.max_rooms, self.feature_dim)
        
        # Apply Sigmoid activation to normalized coordinates [0, 1]
        coords = torch.sigmoid(out[:, :, 0:4])
        # Apply Softmax to room type logits across class channels
        types = torch.softmax(out[:, :, 4:], dim=-1)
        
        return torch.cat([coords, types], dim=-1)
