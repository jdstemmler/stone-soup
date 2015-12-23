#!/bin/bash

cd $CAPSTONE_DIR/data/parsing
python parse_nyt_recipes.py

cd $CAPSTONE_DIR/data/modeling
python make_bag_of_ingredients.py
python topic_modeling.py
