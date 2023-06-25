## Models Downloading

Before running the `full_pipeline.py` file, please make sure you have downloaded the model checkpoints using the following quick URLs (also found in the `model_download_urls.txt` file):

[Longformer-Encoder-Decoder (LED) (3 epochs)](https://huggingface.co/GraceQ/ltb_decision_led/tree/main)

Please download the `led_3epoch_law_allqs.pt`

[LongT5 (3 epochs)](https://huggingface.co/GraceQ/ltb_decision_longt5/tree/main)

Please download the `longT5_3epoch_law_allqs.pt`

## Device Hardware Recommendation

The Large Language Model-based extraction methods require much more computational resources than the rule-based methods, so we recommend having at least the hardware mentioned below to adequately run these extractions.

In the function `get_pred_dataloader`, the `batch_size` is set to 64. It was tested on GPU with 48GB memory. GPU with no less than 48GB memory is recommended to run the `full_pipeline.py` file.

If the GPU memory is smaller than 48GB, a runtime error `CUDA out of memory` can occur. If such an error occures, please use the smaller `batch_size` based on the GPU memory.

## The Model Development 

See `GPT2`, `longformer_qa`, `longformer_encoder_decoder`, `longT5` for the model developing files of GPT-2, Longformer for Question Answering, LED and LongT5.

See directory `preds_llms` for the LLM predictions for the chosen 532 cases.