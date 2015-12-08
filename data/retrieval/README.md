# Data Retrieval

The files in this directory get either recipe metadata or the actual recipes themselves.

Recipe metadata is mostly just recipe names or snippets, as well as the url on the web
where the whole recipe is located. These scripts are called first to get all the metadata
associated with a site. For example, the `get_nytimes_metadata` script crawls through
the NYTimes API to get all the recipes that come back with a "Recipe" type tag. This metadata
then contains the web_url of the actual recipe, which `get_nytimes_recipes` can then use to
download and store the html content of the page.

## Use
`main.sh` can be run to collect all the data. Please note that if you do this, it
will take a couple of days due to the way I have breaks and pauses integrated into the
collection steps. This is so I don't overload the NYTimes API and website and get banned.

## Note:
These scripts simply download data - either json (from an API call) or raw html and put
those results in a MongoDB Database. At this point no scraping happens in this step - this
is purely data collection. This is because with the NYTimes data I can get the web_url
directly from an API call. For more complicated sites, I may need to scrape the metadata
pages to get the URL and then collect the full HTML pages. Scraping and parsing files
can be found in ...