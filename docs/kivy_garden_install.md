# Kivy Garden Matplotlib Installation

To complete the setup, you'll need to install the Kivy Garden matplotlib package. This is a separate step because it requires special permissions.

Run the following commands:

```bash
# Install kivy-garden if not already installed
pip install kivy-garden

# Install matplotlib garden package
# You may need to use sudo depending on your system configuration
garden install matplotlib

# If the above command fails with permission errors, try:
sudo garden install matplotlib

# Alternatively, you can clone the repository manually:
git clone https://github.com/kivy-garden/garden.matplotlib.git
cd garden.matplotlib
pip install .
```

This will install the required Kivy Garden matplotlib package that's needed for the charts and visualization components.
