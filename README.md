REAL
====

These scripts generate keyword, Conceptnet and Stanford NER based features from a given text. This is initially developed for creating feather from problem bodies in ASSISTments but can be used for other text.

Feature generators
------------------
4 different methods were used to generate the features from the problem bodies.

1. Keywords
...The problem body is checked for the presence of user-defined keywords
2. ConceptNet 5
...The problem body is checked for the presence of words related to user-defined concepts. Relationships are inferred from [MIT ConceptNet 5](http://conceptnet5.media.mit.edu/)
3. Stanford Named Entity Recognizer (NER)
...The problem body is checked for the presence of entities defined in the [Stanford NER](http://nlp.stanford.edu/software/CRF-NER.shtml). The entities include place, location, time, person, organization, money, percentage and date.
4. Feature-based features
...Features based on other features can also be created. For example, a *real-world-reference* feature was created by checking for the presence of other features in the problem (i.e., car, animal, person, ...).


Feature generation
------------------
1. Retrieve unique problems from ASSISTments database and store in CSV format.
2. Change the **source** and **target** variables in **driver.py** to control the location of the ASSISTments CSV and the output file location.
3. If needed, modify the **keyword_categories** and **conceptnet_categories** lists in **driver.py* to include other keywords and concepts to be used as features.
4. If needed, modify the **columnval_categories** categories dictionary to create other feature-based features.
5. If needed, modify the **DATA_COL** variable in **driver.py** to the column containing the problem body in the ASSISTments CSV.
7. Performance can be optimized by tweaking the batch and pool size parameters in **driver.py**. *Batch* indicates the number of problems loaded into memory before it is processed. Setting *batch* to 1 would mean running the generators on a single problem, so it is suggested to have a high enough value that would fit in your computer's memory. *pool_size* controls the number of parallel generator processes that would be used. This is highly dependent on your computer so it will need tweaking. A general rule though would be to set *pool_size* to 1 less than the number of processors in your machine.
8. Run using **python driver.py**

Output files
------------
1. history.cfg - stores the last row processed by the script so it can continue processing instead of redoing the entire process whenever unexpected errors are encountered
2. wordmap.json - JSON formatted mapping of words and features used by the generators so it does not have to re-process previously used words

Dependencies
------------
1. [NLTK](http://www.nltk.org/)
2. [Stanford NER](http://nlp.stanford.edu/software/CRF-NER.shtml)
