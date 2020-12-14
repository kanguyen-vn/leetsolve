from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets
from preprocessing.clean import clean_problem, remove_spaces_one
from preprocessing.tokenize_data import tokenize_one
from keras.models import model_from_json
from keras.optimizers import SGD
from keras.preprocessing.text import tokenizer_from_json
from numpy import argmax, amax
from preprocessing.constants import types


class Ui_LeetSolve(object):
    def setupUi(self, LeetSolve):
        model = self.load_model()

        LeetSolve.setObjectName("LeetSolve")
        LeetSolve.resize(804, 518)
        self.centralwidget = QtWidgets.QWidget(LeetSolve)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 781, 431))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(20, 20, 20, 0)
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(30)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.statement_text = QtWidgets.QPlainTextEdit(
            self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(10)
        self.statement_text.setFont(font)
        self.statement_text.setObjectName("statement_text")
        self.verticalLayout.addWidget(self.statement_text)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(50, -1, 50, -1)
        self.horizontalLayout.setSpacing(50)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.preprocess_button = QtWidgets.QPushButton(
            self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.preprocess_button.setFont(font)
        self.preprocess_button.setObjectName("preprocess_button")
        self.horizontalLayout.addWidget(self.preprocess_button)
        self.preprocess_button.clicked.connect(self.preprocess)
        self.predict_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.predict_button.setFont(font)
        self.predict_button.setObjectName("predict_button")
        self.horizontalLayout.addWidget(self.predict_button)
        self.predict_button.clicked.connect(lambda: self.predict(model))
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label_3 = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_3.setFont(font)
        self.label_3.setText("")
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        LeetSolve.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(LeetSolve)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 804, 21))
        self.menubar.setObjectName("menubar")
        LeetSolve.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(LeetSolve)
        self.statusbar.setObjectName("statusbar")
        LeetSolve.setStatusBar(self.statusbar)

        self.retranslateUi(LeetSolve)
        QtCore.QMetaObject.connectSlotsByName(LeetSolve)

    def load_model(self):
        model_path = Path(__file__).parent.absolute() / "model"
        with open(model_path / "model.json", "r") as f:
            model_json = f.read()
        if not model_json:
            raise IOError("Cannot read model")

        model = model_from_json(model_json)
        model.load_weights(model_path / "model.h5")
        model.compile(loss="categorical_crossentropy",
                      optimizer=SGD(lr=0.003), metrics=["accuracy"])
        return model

    def retranslateUi(self, LeetSolve):
        _translate = QtCore.QCoreApplication.translate
        LeetSolve.setWindowTitle(_translate("LeetSolve", "LeetSolve"))
        self.label.setText(_translate("LeetSolve", "LeetSolve"))
        self.label_2.setText(_translate("LeetSolve", "Problem statement:"))
        self.preprocess_button.setText(_translate("LeetSolve", "Preprocess"))
        self.predict_button.setText(_translate("LeetSolve", "Predict"))

    def preprocess(self):
        text = self.statement_text.toPlainText()
        if text.isspace():
            return
        tokenized_text = tokenize_one(remove_spaces_one(text))
        text = "\n".join([" ".join(sentence) for sentence in tokenized_text])
        self.statement_text.setPlainText(text)
        return text

    def predict(self, model):
        text = self.statement_text.toPlainText()
        if text.isspace():
            return
        text = " ".join(self.preprocess().split("\n"))
        model_path = Path(__file__).parent.absolute() / "model"
        with open(model_path / "tokenizer.json", "r") as f:
            tokenizer_json = f.read()
        if not tokenizer_json:
            raise IOError("Cannot read tokenizer")
        tokenizer = tokenizer_from_json(tokenizer_json)
        x = tokenizer.texts_to_matrix([text], mode="binary")
        p = model.predict(x)
        y = argmax(p, axis=-1)
        pred = " ".join([word.capitalize()
                         for word in types[y[0].item()].split("-")])
        prob = f"{round(amax(p, axis=-1)[0].item() * 100, 2)}%"
        self.label_3.setText(f"Prediction: {pred}\nProbability: {prob}")


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    LeetSolve = QtWidgets.QMainWindow()
    ui = Ui_LeetSolve()
    ui.setupUi(LeetSolve)
    LeetSolve.show()
    sys.exit(app.exec_())
