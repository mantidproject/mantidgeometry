This repository is intended to store the python helper scripts for 
generating the Mantid IDFs. Each instrument is supported in its own
python script.

Testing
-------
The test harness is small and will (generically) generate false positives, but you should run it anyway.

1. Do your work and commit it locally
2. `git checkout origin/master` or just `git checkout master` if you did your work on a branch
3. `./test_unchanged.py --setup` will create all the geometry files before you do your work
4. `git checkout -` to go back to your latest commit/branch
5. `./test_unchaged.py` to see what (if anything) has changed

[![Stories in Ready](https://badge.waffle.io/mantidproject/mantidgeometry.png?label=ready)](https://waffle.io/mantidproject/mantidgeometry)

