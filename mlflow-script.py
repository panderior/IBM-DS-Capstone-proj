import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from tqdm import tqdm
import mlflow
import datetime

# helper functions
def train_lr(temp_X_train, temp_X_test, temp_Y_train, temp_Y_test):
    parameters ={"C":[0.01,0.1,1],'penalty':['l2'], 'solver':['lbfgs']}# l1 lasso l2 ridge
    lr=LogisticRegression()
    logreg_cv = GridSearchCV(
        estimator=lr,
        param_grid=parameters,
        cv=10,
        scoring='accuracy',
        verbose=2
    )
    logreg_cv.fit(temp_X_train, temp_Y_train)
    return logreg_cv

def train_svm(temp_X_train, temp_X_test, temp_Y_train, temp_Y_test):
    temp_svm_parameters = {'kernel':('linear', 'rbf','poly','rbf', 'sigmoid'),
              'C': np.logspace(-3, 3, 5),
              'gamma':np.logspace(-3, 3, 5)}
    temp_svm = SVC()

    svm_cv = GridSearchCV(
        estimator=temp_svm,
        param_grid=temp_svm_parameters,
        cv=10,
        scoring="accuracy",
        verbose=2
    )
    svm_cv.fit(temp_X_train, temp_Y_train)

    return svm_cv


def train_tree(temp_X_train, temp_X_test, temp_Y_train, temp_Y_test):
    temp_tree_parameters = {'criterion': ['gini', 'entropy'],
        'splitter': ['best', 'random'],
        'max_depth': [2*n for n in range(1,10)],
        # 'max_features': ['auto', 'sqrt'],
        'max_features': ['sqrt', 'log2'],
        'min_samples_leaf': [1, 2, 4],
        'min_samples_split': [2, 5, 10]
    }

    temp_tree = DecisionTreeClassifier()

    tree_cv = GridSearchCV(
        estimator=temp_tree,
        param_grid=temp_tree_parameters,
        cv=10,
        scoring='accuracy',
        verbose=2
    )
    tree_cv.fit(temp_X_train, temp_Y_train)
    
    return tree_cv

def train_knn(temp_X_train, temp_X_test, temp_Y_train, temp_Y_test):
    temp_knn_parameters = {'n_neighbors': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                'algorithm': ['auto', 'ball_tree', 'kd_tree', 'brute'],
                'p': [1,2]
        }

    temp_KNN = KNeighborsClassifier()

    knn_cv = GridSearchCV(
        estimator=temp_KNN,
        param_grid=temp_knn_parameters,
        cv=10,
        scoring='accuracy',
        verbose=2
    )
    knn_cv.fit(temp_X_train, temp_Y_train)

    return knn_cv

# Run mlflow
if __name__ == '__main__':
    start_time = datetime.datetime.now()
    
    mlflow.set_tracking_uri(uri="http://127.0.0.1:8080/")
    mlflow.set_experiment("Space-X ML Experiment")

    URL1 = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/dataset_part_2.csv"
    data = pd.read_csv(URL1)

    URL2 = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/dataset_part_3.csv'
    X = pd.read_csv(URL2)

    Y = data['Class'].to_numpy()

    transform = preprocessing.StandardScaler()
    X = transform.fit_transform(X)

    lr_name = "Linear Regression"
    svm_name = "SVM"
    tree_name = "Decision Tree"
    knn_name = "KNN"

    models = [
        ("Linear Regression", train_lr),
        ("SVM",               train_svm),
        ("Decision Tree",     train_tree),
        ("KNN",               train_knn),
    ]
    trial_num = 10

    for model_name, train_fn in tqdm(models):
        scores = []
        with mlflow.start_run(run_name=model_name):
            # tag the run so you can filter/group by it in the UI
            mlflow.set_tag("model", model_name)

            for i in range(trial_num):
                Xtr, Xte, ytr, yte = train_test_split(X, Y, test_size=0.2, random_state=i)
                gs = train_fn(Xtr, Xte, ytr, yte)
                test_acc = gs.score(Xte, yte)
                scores.append(test_acc)

                # ── NESTED CHILD RUN ─────────────────────────────────────────
                with mlflow.start_run(run_name=f"{model_name}_trial_{i}", nested=True):
                    # log the best‐params from THIS trial
                    for k, v in gs.best_params_.items():
                        mlflow.log_param(k, v)

                    # log train & test accuracies
                    mlflow.log_metric("train_accuracy", gs.best_score_)
                    mlflow.log_metric("test_accuracy",  test_acc)

                    # log the fitted model artifact
                    mlflow.sklearn.log_model(gs.best_estimator_, artifact_path="model")

            # finally, log the aggregate
            mean_acc = np.mean(scores)
            mlflow.log_param("model", model_name)
            mlflow.log_metric("mean_test_accuracy", mean_acc)

    end_time = datetime.datetime.now()
    print(f"Start time: {start_time}")
    print(f"End time: {end_time}")
    print(f"Training and MLFlow logging Duration: {end_time - start_time}")
