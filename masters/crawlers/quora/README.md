# Quora questions dataset collector based on GeneralizedCrawler

Serves as an example usage of GeneralizedCrawler from `masters.crawlers.abstract`

As you can see from main.py, only two simple routines are defined, so that:

 - an answer text goes to the dataset;
 - profile page and question page doesn't get included in the dataset, but are used for robot's expansion.
 
There's a script in `scripts` for dataset collection.
