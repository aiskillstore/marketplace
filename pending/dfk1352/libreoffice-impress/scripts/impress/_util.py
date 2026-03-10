"""Internal utility helpers for Impress."""


def _cm_to_hmm(cm: float) -> int:
    """Convert centimetres to 1/100 mm (UNO position/size unit)."""
    return int(cm * 1000)
