### Instructions for Using LOKI XML Generator

- run the command `python path/to/generateLOKI.py`. 
- LOKI_definition.xml should be generated in the same folder as the script.
- Launch MantidPlot.
- Run the algorithm LoadEmptyInstrument with path/to/LOKI_definition.xml as the file input.
- The full LOKI geometry should be loaded.
- See script for further documentation on usage.


### Instructions for Using OFF/Instr Generator

- In order to use this generator, a LOKI_definition.xml must have been created from the previous step or otherwise.
- run the command `python path/to/LOKIOFFGenerator.py`.
- The script will generate an OFF file first, then it will use the OFF file for the generation of the McStas Instrument file.