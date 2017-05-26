# Process-flapping-foil-data
Sets up data from a mechanical flapping foil apparatus as a Python class with associated functions.


Functions include: which include: resolving forces to correct coordinate systems (due to rotations of the sensor during pitching movements), filtering data, subtracting corresponding rod data to isolate forces on the foil, providing net and phase averaged values, and saving out processed data.

Flapper_data_analysis.py contains the class structure and function definitions.

Flapper_analysis_wrapper.py contains the commands used to process actual data (for the force trace comparison between laod cell measurements from a flapping foil apparatus and those calculated using a pressure-based technique available at https://github.com/kelseynlucas/Pressure-based-force-calculation-for-foils)
