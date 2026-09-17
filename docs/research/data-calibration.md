# Public Dataset Calibration Workflow

The dataset from Maree et al. (2025) provides climate time-series, control states, and canopy images.

## Import Pipeline
1. Load raw CSV/Image data.
2. Validate using `DataValidator`.
3. Preprocess and map schema to `TwinCurrentState`.
4. Run `ParameterEstimator` to fit `DwarfTomatoModelParameters`.
5. Evaluate using holdout testing on the `SimulationEngine`.

*Note: The dataset itself is not included in this repository due to size and licensing. Researchers must acquire it directly from the original authors' repository.*
