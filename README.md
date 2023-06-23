Allard_A

# Full Pipeline

## Environment and Installation

The codes were tested under Python 3.10.6

Please use the following codes to install the packages in ternimal or command line before running the `.py` file.

`pip install pandas`

`pip install os`

`pip install bs4`

`pip install warnings` 

`pip install re`

`pip install langdetect`

`pip install python-dateutil`

`pip install spacy`

`pip install itertools` 

`pip install numpy`

`pip install gc`

`pip install transformers`

`pip install torch`

## Models Downloading

Before running the `.py` file, please make sure you have downloaded the model checkpoints using the following quick urls:

[Longformer-Encoder-Decoder (LED) (3 epochs)](https://huggingface.co/GraceQ/ltb_decision_led/tree/main)

Please download the `led_3epoch_law_allqs.pt`

[LongT5 (3 epochs)](https://huggingface.co/GraceQ/ltb_decision_longt5/tree/main)

Please download the `longT5_3epoch_law_allqs.pt`

## Device Recommendation

In the function `get_pred_dataloader`, the `batch_size` is set to 64. It was tested on GPU with 48G memory. GPU with no less than 48G memory is recommended to run the `.py` file.

If the GPU memory is smaller than 48G, a runtime error `CUDA out of memory` can occur. If such an error occures, please use the smaller `batch_size` based on the GPU memory.
