import pandas as pd
from sklearn.metrics import accuracy_score, f1_score
from nltk.translate.bleu_score import corpus_bleu
# from rouge_score import rouge_scorer
from nltk.translate.meteor_score import meteor_score

def evaluate(preds_df, gold_df, col_name: str, return_inaccurate: bool = False, metric: str = "accuracy"):
    """
    Evaluates accuracy or other metric between a specified column between the gold_data and silver_data DataFrames.

    Args:
        preds_df (pandas.DataFrame): DataFrame containing the predicted values.
        gold_df (pandas.DataFrame): DataFrame containing the ground truth or gold values.
        col_name (str): Name of the column to compare between the two DataFrames.
        return_inaccurate (bool, optional): Flag indicating whether to return a DataFrame with inaccurate rows (default: False).
        metric (str, optional): Evaluation metric to compute ("accuracy", "f1", "rouge", "bleu", "meteor") (default: "accuracy").

    Returns:
        float or pandas.DataFrame: Evaluation score if `return_inaccurate` is False. DataFrame with inaccurate rows if `return_inaccurate` is True.

    Raises:
        ValueError: If an unsupported `metric` value is provided.

    """
    preds = preds_df[col_name].tolist()
    golds = gold_df[col_name].tolist()

    preds_cols = preds_df.columns.tolist()
    gold_cols = gold_df.columns.tolist()

    if return_inaccurate:
        # Indices of all rows where inaccuracies occur
        inaccurate_inds = [index for index, (x, y) in enumerate(zip(preds, golds)) if x != y]

        # Make a new DataFrame that shows both the gold and silver rows side by side, so inaccuracies can be compared easily

        if metric == "accuracy":
            evaluation_score = accuracy_score(preds, golds)
        # elif metric == "f1":
        #     evaluation_score = f1_score(preds, golds, average = "weighted")
        # elif metric == "rouge":
        #     evaluation_score = calculate_rouge_score(preds, golds)
        # elif metric == "bleu":
        #     evaluation_score = calculate_bleu_score(preds, golds)
        # elif metric == "meteor":
        #     evaluation_score = calculate_meteor_score(preds, golds)
        else:
            raise ValueError(f"Unsupported metric: {metric}")

        preds_df = preds_df.rename(columns={col_name: "silver_" + col_name}).drop(columns=[col for col in preds_cols if col != col_name])
        gold_df = gold_df.rename(columns={col_name: "gold_" + col_name}).drop(columns=[col for col in gold_cols if col != col_name])

        print(evaluation_score)

        return pd.concat([preds_df.loc[inaccurate_inds], gold_df.loc[inaccurate_inds]], axis=1)

    # Compute evaluation score based on the specified metric
    if metric == "accuracy":
        evaluation_score = accuracy_score(preds, golds)
    # elif metric == "f1":
    #     evaluation_score = f1_score(preds, golds, average = "weighted")
    # elif metric == "rouge":
    #     evaluation_score = calculate_rouge_score(preds, golds)
    # elif metric == "bleu":
    #     evaluation_score = calculate_bleu_score(preds, golds)
    # elif metric == "meteor":
    #     evaluation_score = calculate_meteor_score(preds, golds)
    else:
        raise ValueError(f"Unsupported metric: {metric}")

    return evaluation_score

### Example

# evaluate(silver_data, gold_data, "file_number", return_inaccurate = True, metric = "accuracy")

### prints the accuracy score, and then the df of all inaccuracies below it