[![Code Climate](https://codeclimate.com/github/mantidproject/mantidgeometry/badges/gpa.svg)](https://codeclimate.com/github/mantidproject/mantidgeometry)


This repository is intended to store the python helper scripts for 
generating the Mantid IDFs. Each instrument is supported in its own
python script.

Using
-----
The classes that will help with creating geometry are [helper.py](helper.py), [rectangle.py](rectangle.py), and [sns_column.py](sns_column.py). A quick example

```python
from helper import MantidGeom

inst_name = "VISION"

xml_outfile = inst_name+"_Definition.xml"

comment = " Created by G. Fawkes "
valid_from = "2013-11-5 00:00:01"

instr = MantidGeom(inst_name, comment=comment, valid_from=valid_from)
instr.addSnsDefaults(indirect=True)
instr.addComment("SOURCE AND SAMPLE POSITION")
instr.addModerator(-16.0)
instr.addSamplePosition()

instr.writeGeom(xml_outfile)
```

Testing
-------
The test harness is small and will (generically) generate false positives, but you should run it anyway.

1. Do your work and commit it locally
2. `git checkout origin/master` or just `git checkout master` if you did your work on a branch
3. `./test_unchanged.py --setup` will create all the geometry files before you do your work
4. `git checkout -` to go back to your latest commit/branch
5. `./test_unchaged.py` to see what (if anything) has changed

[![Stories in Ready](https://badge.waffle.io/mantidproject/mantidgeometry.png?label=ready)](https://waffle.io/mantidproject/mantidgeometry)

