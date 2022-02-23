from pyAudioAnalysis.audioTrainTest import extract_features_and_train
from pyAudioAnalysis import audioTrainTest as aT
from pyAudioAnalysis import MidTermFeatures as aF
from joblib import dump, load
from pyAudioAnalysis import audioBasicIO as aIO 
import statistics
import os
from sklearn.metrics import confusion_matrix



mt, st = 1.0, 0.05
test_dirs = [r'//home/pi/test_positives/', r'//home/pi/test_negatives/']

model_paths = []
for t in os.listdir(r'//home/pi/trained_models'):
    model_paths.append(r'//home/pi/trained_models/' + t)

for model in model_paths:
    cl = load(model)
    
    x_test = []
    y_test = []
    
    text = model.split("_")
    filecount = 0
    print("Model (" + str(text[2]) + ", " + str(text[3]) + ")")
    for f in os.listdir(test_dirs[0]):
        fs, s = aIO.read_audio_file(test_dirs[0] + f)
        # get mid-term (segment) feature statistics 
        # and respective short-term features:
        mt, st, mt_n = aF.mid_feature_extraction(s, fs, 1 * fs, 1 * fs, 0.05 * fs, 0.05 * fs)
        features = [statistics.mean(mt[int(text[2])]), statistics.mean(mt[int(text[3])])]
        x_test.append(features)
        if cl.predict([features]) == 1:
            print("Predicted: " + str(cl.predict([features])), "     Actual: 1            O")
        else:
            print("Predicted: " + str(cl.predict([features])), "     Actual: 1            X")
        filecount += 1
    y_test += [1]*filecount
  

    filecount = 0
    for g in os.listdir(test_dirs[1]):
        fs, s = aIO.read_audio_file(test_dirs[1] + g)
        mt, st, mt_n = aF.mid_feature_extraction(s, fs, 1 * fs, 1 * fs, 0.05 * fs, 0.05 * fs)
        features = [statistics.mean(mt[int(text[2])]), statistics.mean(mt[int(text[3])])]
        x_test.append(features)
        if cl.predict([features]) == 0:
            print("Predicted: " + str(cl.predict([features])), "     Actual: 0            O")
        else:
            print("Predicted: " + str(cl.predict([features])), "     Actual: 0            X")
        filecount += 1
    y_test += [0]*filecount
    print("Score: " + str(cl.score(x_test, y_test)) + "\n")
    y_pred = cl.predict(x_test)
    print(confusion_matrix(y_test, y_pred))
    print("\n")
    



    #print(f'{f}:')
    #c, p, p_nam = aT.file_classification(f, "svm_test", "svm_rbf")
    #print(f'P({p_nam[0]}={p[0]})')
    #print(f'P({p_nam[1]}={p[1]})')
    #print()

