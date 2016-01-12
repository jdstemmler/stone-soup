# Stone Soup
## Galvanize Capstone Project
### January 2016
### Jayson Stemmler

When I'm not doing data science, one of the things I like to do is cook.
Often times when I finish a recipe I'm left with a handful of leftover
ingredients that I don't quite know how to use up. Because of this, I
decided to make an ingredient-based recipe search tool to help me find
recipes so that my spare ingredients don't go to waste.

## The Story of Stone Soup

Stone soup is an old folk tale where hungry travelers build a meal out of
individual donated ingredients from many of the townsfolk.

> Some travelers come to a village, carrying nothing more than an empty cooking pot. Upon their arrival, the villagers are unwilling to share any of their food stores with the hungry travelers.

> Then the travelers go to a stream and fill the pot with water, drop a large stone in it, and place it over a fire. One of the villagers becomes curious and asks what they are doing. The travelers answer that they are making "stone soup", which tastes wonderful, although it still needs a little bit of garnish to improve the flavor, which they are missing.

> The villager does not mind parting with a few carrots to help them out, so that gets added to the soup. Another villager walks by, inquiring about the pot, and the travelers again mention their stone soup which has not reached its full potential yet. The villager hands them a little bit of seasoning to help them out.

> More and more villagers walk by, each adding another ingredient. Finally, a delicious and nourishing pot of soup is enjoyed by all.

## Stone Stoup in Action

Let's see this in action. If you'd like to play around with it yourself,
head on over to the [Stone Soup](stone-soup.io) webpage and give it a whirl.

When you get there, you'll see the simple web interface:

![Stone Soup homepage](http://stone-soup.s3.amazonaws.com/homepage.png)

The search box takes in a comma separated list of ingredients that you'd like
to search for. Recipe categories can be selected via the check-boxes below the
search box.

The results page presents up to 12 recipes that match the search:

![Stone Soup results](http://stone-soup.s3.amazonaws.com/results.png)

Clicking on a recipe takes the user to the webpage for that recipe in a new tab
where they can do with it what they want.

## Behind the Scenes

There are two main parts to the search and analysis behind Stone Soup:

  1. Recipe aggregation and topic analysis
  2. Matching search terms to recipes

### Recipe Aggregation and Topic analysis

Before a user even visits the site the recipes must be collected, parsed, and
analyzed. For this project I used the entire [New York Times recipe corpus](http://cooking.nytimes.com) (The code is written in such a way that it would be relatively trivial to either substitute for a different recipe site, or add more sources of recipes to provide deeper results). This was accomplished by using the NYTimes article search API to get a list of articles tagged as "recipes," and then downloading the raw HTML content of each recipe into a MongoDB collection.

Each recipe in the corpus was then passed through a [recipe parser](https://github.com/jdstemmler/stone-soup/blob/master/tools/recipetools/parsers/recipe_parsers.py) to extract the relevant details such as name, author, ingredients, directions, nutrition information, notes, and tags. Those that didn't fail (~17,000 out of ~20,000) became the source for my recipe search.

To search for ingredients in the recipes, I created a "bag of ingredients" from the corpus of recipes. This included a column for each ingredient present in the corpus and a row for each recipe. This allows the search tool to look for any ingredient in the corpus and return only those recipes with the requested ingredient in them. More details about the implementation of "search" is described below in the next section.

In addition to creating a "bag of ingredients," I created a "bag of directions" by splitting up the text in the directions into bi- and tri-grams (sequences of two and three words). I then computed the TF-IDF (term frequency - inverse document frequency) matrix for the entire corpus. Finally, I used NMF (non-negative matrix factorization) to decompose the large TF-IDF matrix into eight topics. The end result of this is a matrix that has a row for each recipe and a "strength" value for each of the eight topics. This matrix will be utilized during the search procedure.
