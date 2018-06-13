# Markov Yelp Reviews

Fun with variable length n-grams and Markov Chains in Python!

## About

Yelp produced a dataset of ~ 4 million customer reviews on ~ 15k businesses. I thought it would be interesting to a build model using n-grams and Markov Chains in an attempt to generate fake (but realistic) reviews from Yelp's review corpus. I decided to build the models from scratch to get the project going.

## The Yelp Dataset 

Yelp exposes a subset of its businesses, reviews, and user data for academic and educational purposes. The files come in either SQL or JSON format. Note that the yelp class in this repo expects JSON.

For more info, see: https://www.yelp.com/dataset

## Dependencies

I'm in the process of reorganizing these scripts into a more useable package, so I apologize for the lack of SemVer. But below is what you'd definitely need to get these scripts running.

<div><b><em>Non Python</em></b></div>

* The yelp dataset (~5.5G): https://www.yelp.com/dataset/challenge

<div><b><em>Builtins</em></b></div>

* os
* re
* itertools
* random

<div><b><em>Additional</em></b></div>

* json
* numpy
* pandas
* scipy
* sklearn

## Using this Project

<div><em><b>The Yelp Class</b></em></div>

The YelpData class expects a path to the JSON files from the yelp dataset. On initialization, the yelp class calls internal methods to parse the input JSON and conveniently store information about businesses, users, and reviews. The class is for convenience. It's perfect for someone who wants to apply the Markov class to the yelp dataset without spending time to understand Yelp's JSON structure. That being said, it is restrictive in the sense that the user has no control how the data is reduced and what information is lost in the process.

```python
import os
yelp_path = os.getcwd()
yelp_corpus= YelpData(path)
dir(yelp_corpus) # returns businesses, categories, reviews attributes
```

<div><em><b>The Markov Class</b></em></div>

The MarkovModel class is responsible for actually generating new sentences from the text fed to it. In this project, the corpus consists of yelp reviews, but the MarkovModel accepts any set of documents and is not dependent on yelp data. The code below demonstrates how to initialize the MarkovModel, using the yelp dataset as an example.

```python
yelp_markov = MarkovModel(sentence_vec = yelp_corpus, order = 3)
```

The MarkovModel takes a collection of sentences or documents, which are used as a corpus for the class's sentence generator methods. It also takes an order argument, which specifies the length of the n-grams used as keys in the transition matrix built before generating a random sentence. Three (3) is generally a solid order - anything lower often produces illegible sentences, and numbers higher eventually copy too much one sentence from the original data set.

The MarkovModel class has two methods for generating new sentences. The first is a simple sentence generator, which is fairly naive. The second sentence is (a bit) smarter, reducing some elements of randomness for where the new sentence starts and ends, but still preserving the markov property during state transitions.

## Examples


## Progress

1. Download the yelp dataset and store it locally
2. Build the yelp class as a convenience to extract relavent info from yelp dataset
3. Make markov class independent of the yelp class, allowing any string input
4. Develop second, more advanced setence model so more dynamic than one method

## To Do

This project barely scratches the surface of what can be done with n-grams and Markov chains.  Some directions I'm considering, in addition to other miscellaneous improvements necessary to make the package more useable, are: 

<div><em><b>Yelp</b></em></div>

1. Remove hard-coded dependencies in the yelp class
2. Support SQL files as well for yelp data

<div><em><b>Markov</b></em></div>

1. ~~Make markov class independent of the yelp class, allowing any string input~~
2. ~~Develop second, more advanced setence model so more dynamic than one method~~
3. Use nltk to take care of simple things like creating ngrams
4. Better handling of punctuation and parts-of-speech
5. Weighting words based on metadata and not solely frequency in transition matrix
6. Optimize efficiency of algorithms

<div><em><b>Other</b></em></div>

1. ~Explanation of MarkovModel Class~
2. Examples of flexibility of MarkovModel class and results from yelp dataset.