import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Optional

# Standard Professional Palette (Firefly / Corporate)
DEFAULT_PALETTE = ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#3B1F2B"]

def set_style(theme: str = "professional"):
    """Sets the visual style for plots."""
    sns.set_theme(style="whitegrid")
    if theme == "professional":
        sns.set_palette(sns.color_palette(DEFAULT_PALETTE))
    else:
        sns.set_palette("deep")

    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.labelsize"] = 12
    plt.rcParams["xtick.labelsize"] = 10
    plt.rcParams["ytick.labelsize"] = 10
    plt.rcParams["legend.fontsize"] = 10
    plt.rcParams["figure.figsize"] = (10, 6)
    plt.rcParams["figure.dpi"] = 300

def save_plot(filename: str):
    """Saves the current plot to the specified filename."""
    plt.tight_layout()
    plt.savefig(filename, bbox_inches="tight", dpi=300)
    plt.close()
