# Campaign Monitor 2.0

__Enhanced version of the application to support python2.7, Apache, Bottle-server.__

"Demonstrates use of Twitter APIs, Natural Language Processing, Sentiment Analysis and,
Modelling using Logistic Regression."

Logistic regression has remained one of the best models that describes the randomness of "Nature" with great accuracy. Though decisions taken by public depends on a wide variety of variables (discriptors), it is possible to know whether an inference that we have generated is true (False positives and True Negatives). Therefore an automated script is possible that can precisely tell whether the data collected can really predict with accuracy or not.

The application therefore demonstrate how any model - that is defined after data analysis, can be standardized and automated to make similar experiments reproducible.

There are 5 inputs needed by the system :

* Country
* Keywords(1) that describe the first competing brand/party/entity.
* Keywords(2) that describe the second competing brand/party/entity.
* Start Date - from which the data is collected.
* End Date - until which the data is collected.


Database - name under which all the data is collected for a particular experiment.

These information can be feed into the system to download the data model and create reports on the fly. It is now upto the data scientist to imbue these output values with meaning. When an extra research regarding the data is done, better insightful meaning can be extracted.

 __Note:__

* To start the application locally, you need to start the bottle server on cmdline.
* Before starting however run the trainer.py to create and save tarining algorithms first !!!

Suggestions are always welcome !!!
