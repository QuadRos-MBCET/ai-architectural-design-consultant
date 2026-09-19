import torch
import torch.nn as nn

class ArchitecturalLayoutGenerator(nn.Module):
    """
    Generator Network for a Conditional GAN (cGAN) that generates 
    procedural architectural room layouts (bounding boxes: x, y, w, h).
    """
    def __init__(self, latent_dim=128, num_room_types=15):
        super(ArchitecturalLayoutGenerator, self).__init__()
        
        # Takes a random noise vector (latent space) and a one-hot encoded room type
        self.model = nn.Sequential(
            nn.Linear(latent_dim + num_room_types, 256),
            nn.BatchNorm1d(256),
            nn.LeakyReLU(0.2, inplace=True),
            
            nn.Linear(256, 512),
            nn.BatchNorm1d(512),
            nn.LeakyReLU(0.2, inplace=True),
            
            nn.Linear(512, 1024),
            nn.BatchNorm1d(1024),
            nn.LeakyReLU(0.2, inplace=True),
            
            # Outputs 4 normalized coordinates: [x, y, width, height]
            nn.Linear(1024, 4),
            nn.Sigmoid() # Squashes output between 0.0 and 1.0
        )

    def forward(self, noise, room_labels):
        # Concatenate latent vector and condition labels
        x = torch.cat([noise, room_labels], dim=1)
        layout_box = self.model(x)
        return layout_box


class ArchitecturalLayoutDiscriminator(nn.Module):
    """
    Discriminator Network that judges whether a generated room layout 
    is a "real" (human-drawn) layout or "fake" (AI-generated) based on standard CAD datasets.
    """
    def __init__(self, num_room_types=15):
        super(ArchitecturalLayoutDiscriminator, self).__init__()
        
        self.model = nn.Sequential(
            # Inputs: 4 coordinates [x, y, w, h] + Room Type Label
            nn.Linear(4 + num_room_types, 512),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Dropout(0.3),
            
            nn.Linear(512, 256),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Dropout(0.3),
            
            nn.Linear(256, 1),
            nn.Sigmoid() # Outputs probability (1 = Real, 0 = Fake)
        )

    def forward(self, layout_box, room_labels):
        # Concatenate layout and condition labels
        x = torch.cat([layout_box, room_labels], dim=1)
        validity = self.model(x)
        return validity

# To integrate this into the live app, it must first be trained on a dataset 
# like RPLAN (80,000+ floorplans) using PyTorch, and the trained weights (.pth) 
# must be loaded into llm_service.py to replace the heuristic BSP algorithm.
