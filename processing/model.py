from pathlib import Path
import json
import itertools
import random
import nltk
import math
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_predict, cross_val_score, train_test_split
from sklearn.metrics import f1_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.naive_bayes import MultinomialNB
from sklearn import linear_model, preprocessing
import tensorflow as tf
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Dense, Dropout, Conv1D, GlobalMaxPooling1D, Embedding, SpatialDropout1D, Bidirectional, LSTM, BatchNormalization
from keras.optimizers import SGD, Adam
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def train(src_path, all_texts_json, types):
    all_texts_path = src_path / all_texts_json
    with open(all_texts_path, "r") as f:
        data = json.load(f)

    # all_texts = [problem["content"] for problem in data]
    # # create the transform
    # vectorizer = TfidfVectorizer()
    # # tokenize and build vocab
    # vectorizer.fit(all_texts)
    # # summarize
    # print("Vocabulary")
    # print(vectorizer.vocabulary_, "\n")
    # print(vectorizer.idf_)
    problems = [(problem["content"].split(), problem["label"])
                for problem in data if problem["label"] in types]
    # random.seed(2710)
    # random.shuffle(problems)
    all_words = list(
        set(" ".join([problem["content"] for problem in data]).split()))

    labels = [types.index(problem[1]) for problem in problems]
    problems = [" ".join(problem[0]) for problem in problems]

    problems_train, problems_test, y_train, y_test = train_test_split(
        problems, labels, test_size=0.2, random_state=42, stratify=labels)

    import collections
    y_train_labels = [types[each] for each in y_train]
    y_test_labels = [types[each] for each in y_test]
    print("Train:", collections.Counter(y_train_labels))
    print("Test:", collections.Counter(y_test_labels))
    y_train_hot, y_test_hot = to_categorical(y_train), to_categorical(y_test)

    tokenizer = tf.keras.preprocessing.text.Tokenizer(num_words=len(all_words))
    tokenizer.fit_on_texts(problems_train)

    model_path = Path(__file__).parent.parent / "model"
    with open(model_path / "tokenizer.json", "w") as f:
        json.dump(json.loads(tokenizer.to_json()), f, indent=4)

    X_train = tokenizer.texts_to_matrix(problems_train, mode="binary")
    X_test = tokenizer.texts_to_matrix(problems_test, mode="binary")

    # print("Shape:", X_train[0].shape)
    # print("X_train[0]:", X_train[0])

    # min_max_scaler = preprocessing.MinMaxScaler()
    # X_train, X_test = min_max_scaler.fit_transform(
    #     X_train), min_max_scaler.fit_transform(X_test)

    # print("* SGD:")
    # sgd(X_train, y_train, X_test, y_test)

    # print("* KNN:")
    # for k in range(3, 11):
    #     knn(X_train, y_train, X_test, y_test, k)

    # print("*Random forests:")
    # random_forest(X_train, y_train, X_test, y_test)

    # print("*Naive Bayes:")
    # n_bayes(X_train, y_train, X_test, y_test)

    print("* Neural network:")
    model = ann(X_train, y_train_hot, X_test, y_test_hot,
                vocab_size=len(all_words), maxlen=len(X_train[0]), labelcount=len(types))
    return model


def n_bayes(X_train, y_train, X_test, y_test):
    nb_clf = MultinomialNB()
    nb_clf.fit(X_train, y_train)
    print(nb_clf.score(X_test, y_test))


def sgd(X_train, y_train, X_test, y_test):
    sgd_clf = linear_model.SGDClassifier(loss="huber", random_state=42)
    sgd_clf.fit(X_train, y_train)
    print(sgd_clf.score(X_test, y_test))
    print("CV score:", cross_val_score(
        sgd_clf, X_train, y_train, cv=3, scoring="accuracy"))


def knn(X_train, y_train, X_test, y_test, k=5):
    knn_clf = KNeighborsClassifier(n_neighbors=k)
    knn_clf.fit(X_train, y_train)
    print("KNN with k =", k, ":", knn_clf.score(X_test, y_test))
    y_train_knn_pred = cross_val_predict(knn_clf, X_train, y_train)
    print("F1 score:", f1_score(y_train, y_train_knn_pred, average="weighted"))


def random_forest(X_train, y_train, X_test, y_test):
    rnd_clf = RandomForestClassifier()
    rnd_clf.fit(X_train, y_train)
    print(rnd_clf.score(X_test, y_test))


def ann(X_train, y_train, X_test, y_test, vocab_size, maxlen, labelcount, embedding_dim=64):
    model = Sequential()
    model.add(Dense(90, input_shape=X_train[0].shape, activation="relu"))
    model.add(Dropout(0.2))
    # model.add(Dense(50, activation="relu"))
    # model.add(Dropout(0.2))
    model.add(Dense(labelcount, activation="softmax"))

    # model.add(Embedding(vocab_size, embedding_dim, input_length=maxlen))
    # # model.add(SpatialDropout1D(0.2))
    # model.add(Conv1D(100, 3, activation="relu"))
    # model.add(BatchNormalization())
    # model.add(GlobalMaxPooling1D())
    # model.add(Dense(50, activation="relu"))
    # model.add(Dropout(0.2))
    # model.add(Dense(labelcount, activation="softmax"))

    # model.add(Embedding(vocab_size, embedding_dim, mask_zero=True))
    # model.add(Bidirectional(LSTM(64)))
    # model.add(Dense(64, activation="relu"))
    # model.add(Dense(len(types), activation="softmax"))
    # optimizer = SGD(lr=0.001)
    # initial_learning_rate = 0.1

    # optimizer = SGD(lr=0.003)
    # optimizer = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-8,
    #                  decay=0.01, amsgrad=False)
    model.compile(loss="categorical_crossentropy",
                  optimizer=SGD(lr=0.003), metrics=["accuracy"])

    # def scheduler(epoch, lr):
    #     if epoch < 100:
    #         return lr
    #     else:
    #         return lr * 0.9

    # callback = tf.keras.callbacks.LearningRateScheduler(scheduler)

    history = model.fit(
        X_train,
        y_train,
        epochs=500,
        # callbacks=[callback],
        validation_data=(X_test, y_test),
        verbose=1
    )

    scores = model.evaluate(X_test, y_test, verbose=0)
    print(f"{model.metrics_names[1]} {scores[1] * 100}%")
    model.summary()

    pd.DataFrame(history.history).plot(figsize=(8, 5))
    plt.grid(True)
    # plt.gca().set_ylim(0, 1)
    plt.show()
    return model


def save(model, model_path=None):
    if not model_path:
        model_path = Path(__file__).parent.parent.absolute() / "model"
        model_path.mkdir(exist_ok=True)
    model_json_path = model_path / "model.json"
    model_h5_path = model_path / "model.h5"

    model_json = model.to_json()
    with open(model_json_path, "w") as f:
        json.dump(json.loads(model_json), f, indent=4)
        # f.write(model_json)
    model.save_weights(model_h5_path)
