import pyopenms as ms
import os

def run_workflow(file_path, apply_filter=True):
    """
    Executes a basic MS workflow: Load -> (Optional Filter) -> Peak Access
    
    Args:
        file_path (str): Path to the .mzML or supported MS file.
        apply_filter (bool): Whether to apply a GaussFilter.
        
    Returns:
        dict: Basic statistics or processed data summary.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # 1. Load Data
    exp = ms.MSExperiment()
    print(f"Loading {file_path}...")
    ms.MzMLFile().load(file_path, exp)
    
    # 2. Process (Optional)
    if apply_filter:
        print("Applying GaussFilter...")
        gf = ms.GaussFilter()
        param = gf.getParameters()
        param.setValue("gaussian_width", 0.2)
        gf.setParameters(param)
        gf.filterExperiment(exp)
        
    # 3. Analyze / Extract Data
    # Example: Get first spectrum and peak data
    if exp.getNrSpectra() > 0:
        spec = exp.getSpectrum(0)
        mz, intensity = spec.get_peaks()
        summary = {
            "spectrum_count": exp.getNrSpectra(),
            "first_spectrum_peaks": len(mz),
            "mz_range": (min(mz) if len(mz) > 0 else 0, max(mz) if len(mz) > 0 else 0)
        }
        print(f"Analysis complete: {summary}")
        return summary
    else:
        print("Warning: Experiment contains no spectra.")
        return {"spectrum_count": 0}

if __name__ == "__main__":
    # Example test run
    # run_workflow("test.mzML")
    pass
