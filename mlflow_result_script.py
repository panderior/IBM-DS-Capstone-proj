"""
Author: Duguma Y. (panderior)
Date: August 12, 2025; 4 pm
References:
    - https://medium.com/@zakariae.mkassi/introduction-9c21cc8253b0
    - https://medium.com/analytics-vidhya/retrieving-the-best-model-using-python-api-for-mlflow-7f76bf503692
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import mlflow
from mlflow.entities import ViewType
from tqdm import tqdm
import datetime
import os
import argparse
import humanize

def get_mlflow_individual_result(exp_id, metric):
    runs_df = mlflow.search_runs(experiment_ids=exp_id, run_view_type=ViewType.ACTIVE_ONLY, order_by=[f"metrics.{metric} DESC"])

    # Check if any runs match the specified criteria
    if len(runs_df) == 0:
        raise Exception("No runs found with the given parameters")

    # Find the best run based on the specified metric
    best_model = runs_df.loc[runs_df['metrics.test_accuracy'].idxmax()]
    print("\n-----------")
    print("Best individual model:", best_model["tags.mlflow.runName"])
    print("Test accuracy =", round(best_model[f"metrics.{metric}"], 3))
    # Get params columns only
    params = best_model.filter(like="params.")
    # Filter out None, NaN, or string 'None'
    params = {k: v for k, v in params.items() if pd.notna(v) and str(v) != "None"}
    print("Parameters:")
    for k, v in params.items():
        print(f"  {k} = {v}")
    elapsed = best_model["end_time"] - best_model["start_time"]
    print("Elapsed time: ", humanize.precisedelta(elapsed))


def get_mean_model_acc_helper(df, model_name):
    filtered = df[
        df["tags.mlflow.runName"].str.contains(model_name, na=False)
        & df["metrics.test_accuracy"].notna()
    ]

    if filtered.empty:
        print(f"No {model_name} runs with a test accuracy found.")
        return None

    mean_acc = filtered["metrics.test_accuracy"].mean()
    return mean_acc


def get_mlflow_agg_result(exp_id, metric):
    runs_df = mlflow.search_runs(experiment_ids=exp_id, run_view_type=ViewType.ACTIVE_ONLY)
    
    # Check if any runs match the specified criteria
    if len(runs_df) == 0:
        raise Exception("No runs found with the given parameters")
    
    print("\n-----------")
    print("Mean Model Accuracies")
    print(f"Linear Regression mean {metric} =", round(get_mean_model_acc_helper(runs_df, "Linear Regression"), 3))
    print(f"SVM mean {metric} =", round(get_mean_model_acc_helper(runs_df, "SVM"), 3))
    print(f"Decision Tree mean {metric} =", round(get_mean_model_acc_helper(runs_df, "Decision Tree"), 3))
    print(f"KNN mean {metric} =", round(get_mean_model_acc_helper(runs_df, "KNN"), 3))

    # print(runs_df.columns)

# Run mlflow results
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Get best MLflow result.")
    parser.add_argument("--exp_name", required=True, help="Experiment ID or name")
    parser.add_argument("--metric", required=True, help="Metric name to sort by")
    args = parser.parse_args()

    start_time = datetime.datetime.now()

    mlflow.set_tracking_uri(uri="http://127.0.0.1:8080/")
    mlflow_client = mlflow.tracking.MlflowClient()

    # Get experiment by name
    experiment = mlflow_client.get_experiment_by_name(args.exp_name)
    if experiment is None:
        raise ValueError(f"Experiment '{args.exp_name}' not found.")

    get_mlflow_agg_result(experiment.experiment_id, args.metric)
    get_mlflow_individual_result(experiment.experiment_id, args.metric)

    end_time = datetime.datetime.now()
    print("\n-----------")
    print(f"Start time: {start_time}")
    print(f"End time: {end_time}")
    print(f"MLFlow Result script Duration: {humanize.precisedelta(end_time - start_time)}")