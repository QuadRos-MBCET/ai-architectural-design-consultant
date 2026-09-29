import torch
import torch.nn as nn

class FloorplanCGANDiscriminator(nn.Module):
    """
    Discriminator network for Conditional GAN (CGAN) distinguishing real vs generated floor plan layouts.
    """
    def __init__(self, feature_dim: int = 26, max_rooms: int = 16, cond_dim: int = 24):
        super().__init__()
        self.flat_dim = max_rooms * feature_dim
        
        self.fc_cond = nn.Sequential(
            nn.Linear(cond_dim, 64),
            nn.LeakyReLU(0.2)
        )
        
        self.net = nn.Sequential(
            nn.Linear(self.flat_dim + 64, 256),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )

    def forward(self, x: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        batch_size = x.size(0)
        x_flat = x.view(batch_size, -1)
        cond_feat = self.fc_cond(cond)
        
        h = torch.cat([x_flat, cond_feat], dim=1)
        return self.net(h)
