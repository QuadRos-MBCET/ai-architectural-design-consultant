import torch
import torch.nn as nn

class BuildingBoundaryVAE(nn.Module):
    """
    Variational Autoencoder (VAE) for generating building footprints.
    Encodes architectural parameters into a continuous latent space and decodes 
    them into a structured 2D bounding footprint (Width, Length).
    """
    def __init__(self, input_dim=10, latent_dim=128):
        super(BuildingBoundaryVAE, self).__init__()
        
        # Encoder Network (Maps parameters to Latent Space)
        self.fc1 = nn.Linear(input_dim, 256)
        self.fc2 = nn.Linear(256, 512)
        self.fc_mu = nn.Linear(512, latent_dim)
        self.fc_logvar = nn.Linear(512, latent_dim)
        
        # Decoder Network (Maps Latent Space back to Geometry)
        self.fc3 = nn.Linear(latent_dim, 512)
        self.fc4 = nn.Linear(512, 256)
        self.fc5 = nn.Linear(256, 2) # Outputs (Width, Length) bounds
        
        self.relu = nn.ReLU(inplace=True)

    def encode(self, x):
        h1 = self.relu(self.fc1(x))
        h2 = self.relu(self.fc2(h1))
        # Return Mean and Log-Variance of the latent Gaussian distribution
        return self.fc_mu(h2), self.fc_logvar(h2)

    def reparameterize(self, mu, logvar):
        # Reparameterization trick to allow backpropagation through stochastic nodes
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def decode(self, z):
        h3 = self.relu(self.fc3(z))
        h4 = self.relu(self.fc4(h3))
        # Sigmoid restricts output between 0 and 1, multiply by 100 to map to meters
        return torch.sigmoid(self.fc5(h4)) * 100.0 

    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        decoded_bounds = self.decode(z)
        return decoded_bounds, mu, logvar

# NOTE: For live inference within backend/services/llm_service.py, 
# this requires pre-trained .pth weights.
