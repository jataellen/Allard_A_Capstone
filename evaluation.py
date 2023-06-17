import pandas as pd
from sklearn.metrics import accuracy_score, f1_score
from nltk.translate.bleu_score import corpus_bleu
# from rouge_score import rouge_scorer
from nltk.translate.meteor_score import meteor_score
import jellyfish # for jaro_winkler

def evaluate(preds_df, gold_df, col_name: str, return_inaccurate: bool = False, metric: str = "accuracy", print_score: bool = False):
    """
    Evaluates accuracy or other metric between a specified column between the gold_data and silver_data DataFrames.

    Args:
        preds_df (pandas.DataFrame): DataFrame containing the predicted values.
        gold_df (pandas.DataFrame): DataFrame containing the ground truth or gold values.
        col_name (str): Name of the column to compare between the two DataFrames.
        return_inaccurate (bool, optional): Flag indicating whether to return a DataFrame with inaccurate rows (default: False).
        metric (str, optional): Evaluation metric to compute ("accuracy", "jaro_winkler", "f1", "rouge", "bleu", "meteor") (default: "accuracy").
            If "jaro_winkler", the Jaro-Winkler distance is used to compute the accuracy. If similarity between the pair of values is above 0.7, is counted as accurate to be a match.
            This is reasonable considering things will often not be phrased exactly the same, but will still be usable and could be considered valid.

    Returns:
        float or pandas.DataFrame: Evaluation score if `return_inaccurate` is False. DataFrame with inaccurate rows if `return_inaccurate` is True.

    Raises:
        ValueError: If an unsupported `metric` value is provided.

    """
    if not isinstance(preds_df, list):
        preds = preds_df[col_name].tolist()

    if not isinstance(preds_df, list):
        golds = gold_df[col_name].tolist()

    assert len(preds) == len(golds), "The number of rows in the two DataFrames must be the same."

    preds_cols = preds_df.columns.tolist()
    gold_cols = gold_df.columns.tolist()

    if metric == "accuracy":
        evaluation_score = accuracy_score(preds, golds)
    elif metric == "jaro_winkler":
        total_above_threshold = 0
        for silver, gold in zip(preds, golds):
            if jellyfish.jaro_winkler(str(silver), str(gold)) > 0.6: # values could be something other than a string
                total_above_threshold += 1
        evaluation_score = total_above_threshold / len(preds)
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

    if print_score:
        print(evaluation_score)

    if return_inaccurate:
        # Indices of all rows where inaccuracies occur
        inaccurate_inds = [index for index, (x, y) in enumerate(zip(preds, golds)) if x != y]

        # Make a new DataFrame that shows both the gold and silver rows side by side, so inaccuracies can be compared easily
        preds_df = preds_df.rename(columns = {col_name: "silver_" + col_name}).drop(columns = [col for col in preds_cols if col != col_name])
        gold_df = gold_df.rename(columns = {col_name: "gold_" + col_name}).drop(columns = [col for col in gold_cols if col != col_name])

        return pd.concat([preds_df.loc[inaccurate_inds], gold_df.loc[inaccurate_inds]], axis = 1)

    return evaluation_score

### Example

# evaluate(silver_data, gold_data, "file_number", return_inaccurate = True, metric = "accuracy")

### prints the accuracy score, and then the df of all inaccuracies below it