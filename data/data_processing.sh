#!/bin/bash

# cd $CAPSTONE_DIR/data/parsing
# python parse_nyt_recipes.py

# make pickles out of the bag of ingredients and topic modeling
cd $CAPSTONE_DIR/data/modeling
echo "Processing Bag of Ingredients"
python make_bag_of_ingredients.py

echo "Performing Matrix Factorization"
python topic_modeling.py

echo "Complete"