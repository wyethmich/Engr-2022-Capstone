#!/usr/bin/env python
# coding: utf-8

# In[1]:


##### Example5: plot 2 features for 10 2-second samples 
from pyAudioAnalysis import MidTermFeatures as aF
import os
import numpy as np
from sklearn.svm import SVC
import plotly.graph_objs as go 
import plotly
import soundfile as sf
from pyAudioAnalysis import MidTermFeatures as aF
from pyAudioAnalysis import audioBasicIO as aIO 
import statistics
import matplotlib.pyplot as plt
from joblib import dump, load

PLOT = False

train_dirs = [r'//home/pi/train_positives', r'//home/pi/train_negatives'] 
test_dirs = [r'//home/pi/test_positives', r'//home/pi/test_negatives']

class_names = ["positive", "negative"] 
m_win, m_step, s_win, s_step = 1, 1, 0.1, 0.05 

features = [] 
max_acc = 0
best_i = 0
best_j = 0

best_i_list, best_j_list = [1, 2, 3, 6, 14, 24, 27, 28, 28, 28, 35, 36, 40, 46, 46, 46, 46, 48, 56, 60, 62, 63, 64, 66, 77, 77, 77, 86, 86, 87, 90, 90, 90, 92, 93, 95, 95, 96, 99, 101, 101, 101, 108, 119, 124, 124, 129, 130, 131, 135, 135, 135, 135, 135, 135, 135, 135, 135, 135, 135, 135, 135, 135, 135], [24, 77, 14, 135, 3, 90, 86, 13, 135, 131, 135, 124, 135, 96, 101, 130, 135, 135, 135, 135, 135, 135, 135, 135, 2, 95, 99, 27, 129, 101, 24, 92, 135, 90, 119, 77, 101, 46, 77, 46, 87, 95, 135, 93, 36, 135, 86, 46, 28, 6, 28, 35, 40, 46, 48, 56, 60, 62, 63, 64, 66, 90, 108, 124]
for d in train_dirs: # get feature matrix for each directory (class) 
    f, files, fn = aF.directory_feature_extraction(d, m_win, m_step, s_win, s_step) 
    features.append(f)

for m in range(len(best_i_list)):
    i = best_i_list[m]
    j = best_j_list[m]
    try:
        x_test = []
        y_test = []
        ######### Initialize positive testing data #########
        filecount = 0
        for q in os.listdir(test_dirs[0]):
            fs, s = aIO.read_audio_file(test_dirs[0] + "/" + q)
            # get mid-term (segment) feature statistics
            # and respective short-term features:
            mt, st, mt_n = aF.mid_feature_extraction(s, fs, 1 * fs, 1 * fs, 0.05 * fs, 0.05 * fs)
            x_test.append((statistics.mean(mt[mt_n.index(fn[i])]), statistics.mean(mt[mt_n.index(fn[j])])))
            filecount += 1
        y_test += [1]*filecount

        filecount = 0
        for u in os.listdir(test_dirs[1]):
            fs, s = aIO.read_audio_file(test_dirs[1] + "/" + u)
            mt, st, mt_n = aF.mid_feature_extraction(s, fs, 1 * fs, 1 * fs, 0.05 * fs, 0.05 * fs)
            x_test.append((statistics.mean(mt[mt_n.index(fn[i])]), statistics.mean(mt[mt_n.index(fn[j])])))
            filecount += 1
        y_test += [0]*filecount
    except:
        continue
    slices = list(zip(*x_test))
    print(x_test, y_test)
    f1 = np.array([features[0][:, i],
                           features[0][:, j]])
    f2 = np.array([features[1][:, i],
                           features[1][:, j]])

    y = np.concatenate((np.ones(f1.shape[1]), np.zeros(f2.shape[1]))) 
    f = np.concatenate((f1.T, f2.T), axis = 0)

    # train the svm classifier
    cl = SVC(kernel='rbf', C=20) 
    cl.fit(f, y) 

    score = cl.score(x_test, y_test)
    for g in range(20):
        print("Actual: " + str(y_test[g]) + "\n" + "Predicted: " + str(cl.predict([x_test[g]])))
    print("Score (" + str(i) + ", " + str(j) + "): " + str(score))
    if score >= 0.9:
        dump(cl, r'//home/pi/trained_models/' + str(score) + "_" + str(i) + "_" + str(j) + "_svc.joblib")
        max_acc = score
        print(score)
        print(i, j)

