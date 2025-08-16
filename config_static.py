# Configuration for STATIC dataset mode
DATA_PATH = "data/bond_dataset.csv"
STATIC_MODE = True  # no price updates or rebalancing

def get_dataset_path():
    """Return the fixed dataset path for the challenge."""
    return DATA_PATH

def is_static_mode():
    """Return True if static mode is active."""
    return STATIC_MODE
