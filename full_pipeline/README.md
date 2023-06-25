## Environment and Installation

All code was tested under Python 3.10.6.

To Install the necessary dependencies for the project, navigate to this directory in your command line and use `pip install -r requirements.txt`

## Full Pipeline

This directory contains the code for the entire extraction pipeline. The pipeline uses a combination of Rule-Based methods and Large Language Model-methods. To use the pipeline, first ensure all libraries from the requirements.txt file in the main directory have been installed. Place the HTML file of each respective case downloaded directly from the CanLII website into the `pipeline_input` directory. Note that the directory currently contains 6 examples to illustrate how the files should look and that **the names of the HTML files themselves do not matter**, as the file names are considered or used at all in the pipeline. All information is taken directly from the contents of the file. Next, navigate to this directory in your command line, and use the command `python full_pipeline.py`. If done correctly, the `pipeline_output` directory should then be populated with a `extracted_info.csv` file. This won't be very readable to humans (and opening this file in a program like Micrsoft Excel may show errors, since there are very large sequences of text and other Python-specific datatypes that Excel is not built to handle). This file can be used to update the database, or can be used to feed into the case predictions model, depending on how those systems are setup. 

## Models Downloading

Before running the `full_pipeline.py` file, please make sure you have downloaded the model checkpoints using the following quick URLs (also found in the `model_download_urls.txt` file):

[Longformer-Encoder-Decoder (LED) (3 epochs)](https://huggingface.co/GraceQ/ltb_decision_led/tree/main)

Please download the `led_3epoch_law_allqs.pt`

[LongT5 (3 epochs)](https://huggingface.co/GraceQ/ltb_decision_longt5/tree/main)

Please download the `longT5_3epoch_law_allqs.pt`

## Device Hardware Recommendation

The Large Language Model-based extraction methods require much more computational resources than the rule-based methods, so we recommend having at least the hardware mentioned below to adequately run these extractions.

In the function `get_pred_dataloader`, the `batch_size` is set to 64. It was tested on GPU with 48GB memory. GPU with no less than 48GB memory is recommended to run the `full_pipeline.py` file.

If the GPU memory is smaller than 48GB, a runtime error `CUDA out of memory` can occur. If such an error occurs, please use the smaller `batch_size` based on the GPU memory.