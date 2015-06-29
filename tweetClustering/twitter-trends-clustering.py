# -*- coding: utf8 -*-
"""
Using twitterAPI and sklearn, clusters the hashtag and at mentions according to semantic similarity.
In order to determine the best K for the clustring, use silhouette score as a metric.  
"""
from twitterAPI import TwitterAPI
from sklearn.feature_extraction.text import TfidfTransformer, TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn import metrics
from sklearn.metrics import silhouette_score
import numpy as np

# Read trends from csv file
trends = []
with open('trends.csv') as f:
    for t in f.read().split(','):
        trends.append((t.strip().lower()))

# Print ">> Retrieving tweets".
api = TwitterAPI()
corpus = []
for hashtag in trends:
    corpus.append('. '.join(api.search(hashtag)))

vectorizer = TfidfVectorizer()

term_document_matrix = vectorizer.fit_transform(corpus)
tf_transformer = TfidfTransformer(use_idf=True).fit(term_document_matrix)
term_document_matrix_tf = tf_transformer.transform(term_document_matrix)

# Set lower bound by rule of thumb for determining k using the silhouette coefficient.
num_clusters_lower = int(np.sqrt(len(trends) / 2))
num_clusters_upper = int(len(trends))
print "lower k bound is: %s and upper k bound is %s" % (num_clusters_lower, num_clusters_upper)
best_k = num_clusters_lower
silhouette_avg = -1.0
labelsFinal = []

# Brute forcefully determine the k by finding a maximal silhouette score.     
for current_k in range(num_clusters_lower, num_clusters_upper):
    km = KMeans(n_clusters=current_k, max_iter=50, n_init=1, random_state=1)
    labels = km.fit_predict(term_document_matrix_tf)
    silhouette_avg_for_k = silhouette_score(term_document_matrix_tf, labels)
    print "silhouette score average is: %s" % silhouette_avg_for_k
    if silhouette_avg_for_k > silhouette_avg:
        best_k = current_k
        silhouette_avg = silhouette_avg_for_k
        labelsFinal = labels

print "best k is: %s and highest silhouette score is: %s" % (best_k, silhouette_avg)

# Build cluster > list of tags dict.
clusters = {}
for i, c in enumerate(labelsFinal):
    if not c in clusters:
        clusters[c] = []
    clusters[c].append(trends[i])

# Display the result.
print ">> Results:"
for c, tags in clusters.iteritems():
    print "[%d]: %s" % (c, ', '.join(tags))
    print 'cluster size: %d' % len(tags)
