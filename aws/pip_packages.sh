#!/usr/bin/env bash

pip install --upgrade ipython
pip install --upgrade jupyter
pip install --upgrade numpy scipy
pip install --upgrade matplotlib
pip install --upgrade scikit-learn
pip install --upgrade beautifulsoup4
pip install --upgrade flask
pip install --upgrade requests
pip install --upgrade pymongo

pip install -e $CAPSTONE_DIR/tools