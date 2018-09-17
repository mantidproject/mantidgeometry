# ILL geometries

## Instrument definitions for D11, D22, D33, D17, FIGARO

The `IDF` folder contains Python scripts to create XML instrument definition files.
If you wish to generate an instrument defintion file (IDF) for an ILL instrument, you can use the scripts in the following way:

1. Change to the `mantidgeometry` directory 
2. `./test_unchaged.py` will create all instrument definitions.
3. Change back to folder `ILL\IDF` and select the IDF of your choice.

Please note that some scripts can create instrument defitions of different resolution.
The script may be changed to produce a different resolution IDF for D11 and D22.
Consider to not store a particular resolution script in this repository since `./test_unchanged.py --setup` will not create `*_master.xml` files for testing.

## Other Instruments definitions

Please consult the Python scripts directly for IN4, IN5, IN6, IN16B, D4, D1B, D2B, D20. 
