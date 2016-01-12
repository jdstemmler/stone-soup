#!/usr/bin/env python

import os
import pickle
from sklearn.decomposition import NMF


def model_topics(directions):
    nmf = NMF(max_iter=600, n_components=8, verbose=1)
    nmf.fit(directions)
    W, H = nmf.transform(directions), nmf.components_

    return W, H


if __name__ == "__main__":

    # set the location of the settings file
    cap_dir = os.getenv("CAPSTONE_DIR")
    settings_file = os.path.join(cap_dir, 'settings', 'project_settings.json')

    # set the pickle file
    features_file = os.path.join(cap_dir, 'data/pickles/features.pkl')
    topics_file = os.path.join(cap_dir, 'data/pickles/topics.pkl')

    with open(features_file, 'rb') as f:
        features = pickle.load(f)

    directions = features['directions_tfidf']
    W, H = model_topics(directions)
    with open(topics_file, 'wb') as f:
        pickle.dump({'W': W, 'H': H}, f)
