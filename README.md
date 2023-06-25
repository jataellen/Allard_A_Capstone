# Allard_A

## Environment and Installation

All code was tested under Python 3.10.6.

To Install the necessary dependencies for the project, navigate to this directory in your command line and use `pip install -r requirements.txt`

## Web App

This directory contains all code for the code back-end and front-end of the annotations web app.

## Full_Pipeline

This directory contains all both the code building and the Python script for the extraction methods used in this project. See the directory for more information on how to run this code and extract information from files.

## Models

This directory contains information on the development and implementation of the Large Language Model (LLM)-based methods used in this project. See the directory for more specific information on installation instructions and hardware recommendations to run them.

## Device Hardware Recommendation

The Large Language Model-based extraction methods require much more computational resources than the rule-based methods, so we recommend having at least the hardware mentioned below to adequately run these extractions.

In the function `get_pred_dataloader`, the `batch_size` is set to 64. It was tested on GPU with 48GB memory. GPU with no less than 48GB memory is recommended to run the `full_pipeline.py` file.

If the GPU memory is smaller than 48GB, a runtime error `CUDA out of memory` can occur. If such an error occures, please use the smaller `batch_size` based on the GPU memory.

## Scraping

The contents of this directory code was initally used to gather data for to develop the extractions methods used within the project. This code should not need to be run again, but was included in this repository to have a record of case files were collected, and for it to be possible should the database need to be created from scratch once again, however this is not recommended (it is a time-intensive process and may require some manual intervention).

The contents of the `Scraping.zip` file is the result of this code, containing all cases scraped from CanLII, with each case in both an HTML format and a `.txt` format. See the `full_pipeline` directory for more information on how to use these files to extract information from them.
