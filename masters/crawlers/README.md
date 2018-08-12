# Dataset storage

I'll try to follow a single format for all datasets I obtain in this section.

Every dataset is stored as a JSON list with dicts as elements. Each dict may contain the following fields:

 - **content_raw** : the content of the article "as is", basically a piece of HTML-code
 - **content_clean** : an attempt to create something like pure text from the HTML mess; you shouldn't be 100%-confident in it. Basically it's just a set of heuristics applied to the raw content. In some cases they should be enough though (WP dataset, for instance).
 - **title_raw** : the title of the article "as is", may contain special characters or whatever
 - **title_clean** : clean title of the article
 - **tags** : the set of cannonized tags. Tag cannonization consists of removing leading hashtag signs and lowercasing.


