# Dataset acquisition

## In brief

### Corner cases

WordPress crawler solves the partial case with very good dataset quality. It crawls only English articles at WordPress.com and fetches article as a text and tags as keywords.

Wiki crawler is also pretty OK. It downloads random articles in the chosen language. Then you can use any third-party API for labelling. I've used Cortical: http://www.cortical.io/extract-keywords.html

### General case

Abstract crawler is not itself a dataset collector. It's a generalization over dataset collectors, which uses basic search robot to crawl a website and pick pages matching the chosen rule as dataset elements.

The example usage of an abstract crawler is Quora crawler.

## Storage protocol

I'll try to follow a single format for all datasets I obtain in this section.

Every dataset is stored as a JSON list with dicts as elements. Each dict may contain the following fields:

 - **content_raw** : the content of the article "as is", basically a piece of HTML-code
 - **content_clean** : an attempt to create something like pure text from the HTML mess; you shouldn't be 100%-confident in it. Basically it's just a set of heuristics applied to the raw content. In some cases they should be enough though (WP dataset, for instance).
 - **title_raw** : the title of the article "as is", may contain special characters or whatever
 - **title_clean** : clean title of the article
 - **tags** : the set of cannonized tags. Tag cannonization consists of removing leading hashtag signs and lowercasing.


