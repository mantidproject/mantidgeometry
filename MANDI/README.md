# From DetCal to MANDI Geometry

To create an IDF file:

```bash
cd MANDI
./MANDIFromDetCal.py
# It will ask for the *.DetCal filename
#
# The generated files have the format:
# MANDI_*.xml
```

To test the new instrument, copy the generated files to:
```
$HOME/.mantid/instrument/
```

Start mantid, either use the Algorithm `LoadEmptyInstrument` and load the generated `MANDI_Definition_*.xml`, or load some data and keep an eye on log (use DEBUG Level). You should see:
```
IDF selected is /SNS/users/<username>/.mantid/instrument/MANDI_Definition_<file date>.xml
```
