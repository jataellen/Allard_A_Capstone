import pandas as pd # for everthing
import os # for finding/directing files
from bs4 import BeautifulSoup # for parsing html
import warnings # to stop warnings from being shown in command line output
import re # for most things

### for detecting language
# !pip install langdetect
from langdetect import detect

### for date thing
from dateutil.parser import parse
import spacy
nlp = spacy.load("en_core_web_sm")

# Filter or ignore specific warning types
warnings.filterwarnings("ignore")

import itertools # for making iterating easier

import numpy as np
# ! pip install gc
import gc  # for saving GPU RAM

# ! pip install transformers
from transformers import AutoTokenizer
from transformers import AutoModelForSeq2SeqLM

import torch
from torch import cuda, nn, optim
from torch.utils.data import Dataset, DataLoader
from torch.nn.utils.rnn import pad_sequence

manual_seed = 595     # can be changed to any random number
torch.manual_seed(manual_seed)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")   
# The models require a lot of compute resouce and need to be run on GPUs
print(device)
# The output shall be `cuda` to run the models

input_dir = "pipeline_input/"

files_dict = {}
files_dict['raw_file_str'] = []

for file in os.listdir(input_dir):
    try:
        if os.path.isfile(input_dir + file) and not file.startswith('.') and file.endswith('.html'): # will only work for non-system files that are .html files
            # print("Adding ", file, "...")
            with open(input_dir + file) as f:
                html = f.read()
            soup = BeautifulSoup(html, "html.parser")

            # find metadata
            document_meta = soup.find("div", {"id": "documentMeta"}) 
            meta_items = document_meta.find_all("div", {"class": "row py-1"})

            # "Metadata"
            case_ID = ""
            meta_data = []
            for meta_item in meta_items:
                children_text = []
                for x in meta_item.findChildren()[:2]:
                    children_text.append(x.text)
                child_string = '\t'.join(children_text)
                if "file number" in child_string.lower():
                    case_ID = child_string.split("\t")[1].strip()
                    # print(case_ID)
                meta_data.append(child_string)

            # "Content"
            document_body = soup.find("div", {"class": "documentcontent"}).get_text()

            # add to raw_files_dict{} to be put into dataframe later
            files_dict['raw_file_str'].append('Metadata:\n' +          # metadata marker
                                               '\n'.join(meta_data) +   # metadata text
                                               'Content:\n' +           # content marker
                                               document_body)           # content text
            
    except:
        print("Error with:", file)

data_df = pd.DataFrame(files_dict)

def general_cleaning(raw_file_str: str):
    """
    Performs general cleaning on a raw file string.

    This function removes tabs, non-breaking spaces, leading/trailing whitespace, empty lines, 
    and "\xa0" characters. This function operates line-by-line for the input text and only keeps 
    non-empty lines after stripping.

    Parameters
    ----------
    raw_file_str : str
        The raw file content as a string, where different lines are separated by '\n'.

    Returns
    -------
    list
        A list of cleaned lines. Each element of the list is a cleaned string corresponding to a non-empty 
        line in the input string. Tabs and "\xa0" characters are replaced with spaces, leading/trailing 
        whitespaces are removed.

    Examples
    --------
    >>> general_cleaning("  First line \t \n \xa0 \nSecond line \n   Third line\t")
    ['First line', 'Second line', 'Third line']
    """

    # gets rid of tabs, non-breaking spaces, leading/trailing whitespace, removes empty lines, and "\xa0"
    generally_cleaned_list = [line.replace("\t", " ").replace("\xa0", "").strip() for line in raw_file_str.split('\n') if line.strip() != '']
    return generally_cleaned_list

def remove_whitespace_and_underscores(string):
    """
    Removes consecutive whitespace and more than three consecutive underscores from a given string.
    
    Parameters
    ----------
    string : str
        The input string to be processed.
        
    Returns
    -------
    str
        The processed string with consecutive whitespace and more than three consecutive underscores removed.
    
    Examples
    --------
    >>> remove_whitespace_and_underscores("Hello    world___")
    'Hello world'
    
    >>> remove_whitespace_and_underscores("   This    string_has___many____underscores  ")
    'This string_has_many_underscores'
    """
    # Remove consecutive whitespace
    string = re.sub(r'\s+', ' ', string)

    # Remove more than three consecutive underscores
    string = re.sub(r'_+', '', string)

    return string.strip()

def separate_file_sections(text_with_newlines: str):
    metadata_list = []
    content_list = []

    is_metadata = True
    is_content = False

    cleaned_full_file = general_cleaning(text_with_newlines)

    for line in text_with_newlines.split("\n"):
        if line.strip() == 'Metadata:':
            is_metadata = True
            is_content = False
        elif line.strip() == 'Content:':
            is_metadata = False
            is_content = True
        elif is_metadata:
            metadata_list.append(remove_whitespace_and_underscores(line))
        elif is_content:
            content_list.append(remove_whitespace_and_underscores(line))

    return "\n".join(cleaned_full_file).strip(), " ".join(cleaned_full_file).strip(), " ".join(metadata_list).strip(), " ".join(content_list).strip()

for row in data_df.index:
    full_raw_text = data_df.loc[row, 'raw_file_str']

    # full_file, case_metadata, case_content = extract_metadata_t5(
    #     raw_case_file_text = full_raw_text,
    #     model = model,
    #     tokenizer = tokenizer)
    
    for_txt_file, full_file_str, case_metadata, case_content = separate_file_sections(full_raw_text)
    
    data_df.loc[row, 'cleaned_case_with_newlines'] = for_txt_file
    data_df.loc[row, 'full_file'] = full_file_str
    data_df.loc[row, 'metadata'] = case_metadata
    data_df.loc[row, 'content'] = case_content

def get_case_citation(metadata_list):
    """
    Extracts the case citation from a list of metadata lines.

    This function searches through the metadata lines for a line containing "Citation:" or "Référence:"
    and extracts the citation information from that line.

    Parameters
    ----------
    metadata_list : list of str
        A list of metadata lines.

    Returns
    -------
    str or None
        The extracted case citation, or None if no citation is found.

    Examples
    --------
    >>> metadata = ["Title: Example Case", "Citation: ABC123 (LTB)"]
    >>> get_case_citation(metadata)
    'ABC123 (LTB)'

    >>> metadata = ["Title: Another Case", "Référence: XYZ789 (LTB)"]
    >>> get_case_citation(metadata)
    'XYZ789 (LTB)'
    """
    if isinstance(metadata_list, str):
        metadata_list = metadata_list.split("\n")

    for line in metadata_list:
        if "Citation:" in line:
            citation_start = line.find("Citation: ")
            citation_end = line.find("LTB)") + 4
            return line[citation_start:citation_end].replace("Citation: ", "").strip()
        elif "Référence: " in line:
            citation_start = line.find("Référence: ")
            citation_end = line.find("LTB)") + 4
            return line[citation_start:citation_end].replace("Référence: ", "").strip()
    return None

def get_file_number(metadata_list):
    """
    Extracts the file number from a list of metadata lines.

    This function concatenates the metadata lines into a single string and extracts the file number
    from that string. The file number is obtained either after "File number:" or "Numéro de dossier:".

    Parameters
    ----------
    metadata_list : list of str
        A list of metadata lines.

    Returns
    -------
    str or None
        The extracted file number, or None if no file number is found.

    Examples
    --------
    >>> metadata = ["File number: TNL-10001-18", "Citation: ABC123 (LTB)"]
    >>> get_file_number(metadata)
    'TNL-10001-18'

    >>> metadata = ["Numéro de dossier: XYZ789", "Référence: DEF456 (LTB)"]
    >>> get_file_number(metadata)
    'XYZ789'
    """
    if isinstance(metadata_list, list):
        metadata_str = " ".join(metadata_list)
    else:
        metadata_str = metadata_list

    if "Citation: " in metadata_str:
        file_nums = metadata_str[metadata_str.find("File number: ") + len("File number: ") : metadata_str.find("Citation:")].strip()
    elif "Référence: " in metadata_str:
        file_nums = metadata_str[metadata_str.find("Numéro de dossier: ") + len("Numéro de dossier: ") : metadata_str.find("Référence")].strip()

    if len(file_nums) == 0:
        return None

    file_nums = file_nums.replace(";", " ")

    file_num = list(set(file_nums.split()))
    file_num = ";".join(file_num)
    file_num = re.sub(r'[^\w\s]$', '', file_num)

    if ";" in file_num:
        file_num = list(set(file_num.split(";")))
        file_num = [re.sub(r'[\(\)]', '', num) for num in file_num]
        file_num = ";".join(file_num)

    file_num = re.sub(r'[\(\)]', '', file_num)

    return file_num

def is_mostly_french(text, threshold):
    try:
        detected_language = detect(text)
        if detected_language == 'fr':
            return True
        else:
            return False
    except:
        return False

def is_french(text, threshold):
    try:
        detected_language = detect(text)
        if detected_language == 'fr':
            return True
        language_probabilities = detect_langs(text)
        for lang in language_probabilities:
            if lang.lang == 'fr' and lang.prob > threshold:
                return True
        return False
    except:
        return False
    
for row in data_df.itertuples():

    # adding to 'language' column
    if is_french(data_df.loc[row.Index, "raw_file_str"], 0.7) == True:
        data_df.at[row.Index, 'language'] = "French"
    else:
        data_df.at[row.Index, 'language'] = "English"

year_pattern = r"\b(\d{4})\b"

for row in data_df.itertuples():

    year_match = re.search(year_pattern, data_df.loc[row.Index, "metadata"])
    if year_match:
        year = year_match.group(1)
        data_df.loc[row.Index, "year"] = year
    else:
        data_df.loc[row.Index, "year"] = "year not found"

def find_all_positions(text: str, keyword: str):
    """
    Finds all positions of a keyword in a given text.

    This function searches for a keyword in a given text and returns a list of positions where the keyword is found.

    Parameters
    ----------
    text : str
        The text to search within.
    keyword : str
        The keyword to find in the text.

    Returns
    -------
    list
        A list of integers representing the positions of the keyword in the text.

    Examples
    --------
    >>> find_all_positions("This is an example sentence.", "example")
    [11]
    """
    positions = []
    start = 0
    while True:
        index = text.find(keyword, start)
        if index == -1:
            break
        positions.append(index)
        start = index + 1
    return positions

def get_postal_code(text: str):
    """
    Finds a postal code in the format "L4Z2G5" within the given text.

    Args:
        text (str): The input text to search for a postal code.

    Returns:
        str: The postal code found in the text. Returns an empty string if no postal code is found.

    Examples:
        >>> find_postal_code("This is a sample text with a postal code L4Z2G5.")
        "L4Z2G5"
    """

    pattern = r"\b[A-Za-z]\d[A-Za-z]\d[A-Za-z]\d\b"
    match = re.search(pattern, text)

    if match:
        return match.group()
    else:
        return None

def find_closest_subset(text: str, keywords: list):
    """
    Finds a subset of the given text where a date and any of the given keywords appear with the smallest distance between them,
    but only if the subset appears before the word "determination" in the lowercase text and does not contain the word "member".

    Args:
        text (str): The input text to search for the subset.
        keywords (list): The list of keywords to search for.

    Returns:
        tuple: A tuple containing the subset of the text where the date and keyword appear with the smallest distance between them,
               and the corresponding keyword. Returns an empty string and None if no match is found or if the subset appears after "determination"
               or contains the word "member".

    Examples:
        >>> find_closest_subset("The event will take place on April 23, 2018. The application was heard on April 25, 2018.", ["heard", "event"])
        ("The event will take place on April 23, 2018.", "event")

    """

    pattern = r"\b[A-Z][a-z]+ \d{1,2}, \d{4}\b"
    date_matches = re.findall(pattern, text)
    keyword_positions = [(m.start(), m.end(), keyword) for keyword in keywords for m in re.finditer(keyword, text)]

    if not date_matches or not keyword_positions:
        return "", None

    smallest_distance = float('inf')
    best_subset = ""
    best_keyword = None
    
    for date in date_matches:
        for start, end, keyword in keyword_positions:
            distance = abs(start - text.find(date))
            subset = text[min(start, text.find(date)): max(end, text.find(date))]

            if distance < smallest_distance and text.lower().find(best_subset.lower()) < (text.lower().find("determination") or text.lower().find("it is determinatined that")) and ("member" or "with the request to review") not in subset.lower():
                smallest_distance = distance
                best_subset = subset
                best_keyword = keyword

    if text.lower().find(best_subset.lower()) >= text.lower().find("determination") or "member" in best_subset.lower():
        return "", None

    return best_subset, best_keyword


def get_ltb_location_by_postal_code(case_content_str: str):
    """
    Helps to extract the location information from the given case content string using postal code lookup.

    Args:
        case_content_str (str): The case content string to extract the location from.

    Returns:
        str or None: Subset of text from the passed case string wherein the location appears near the postal code.

    Examples:
        >>> get_ltb_location_by_postal_code("The application was heard at L4Z 2G5.")
        "Mississauga"
    """

    # if there isn't a postal code, return None right away
    if not get_postal_code(case_content_str):
        return None

    pc_idx = case_content_str.find(get_postal_code(case_content_str))
    subset = case_content_str[pc_idx - 30 : pc_idx]

    if "ON" in subset:
        subset = subset.split("ON")[:-1]
    elif "Ontario" in subset:
        subset = subset.split("Ontario")[:-1]

    subset = " ".join(subset)
    
    if "floor" in subset.lower():
        floor_idx = subset.lower().find("floor")
        # print(floor_idx)
        subset = subset[floor_idx + len("floor") :].strip()
    
    return subset

def get_ltb_location(case_content_str: str):
    """
    Extracts the location information from the given case content string.

    Args:
        case_content_str (str): The case content string to extract the location from.

    Returns:
        str or None: The extracted location information if found, otherwise None.

    Examples:
        >>> get_ltb_location("The application was heard in Newmarket.")
        "Newmarket"
    """

    keywords = ["application was heard", "applications were heard", "was heard", "were heard together",
                "was held", "set to be heard",
                # "heard by telephone", "heard by teleconference", "heard via teleconference",
                "heard by", "heard by", "heard via",
                "motion were heard", "motion was heard", "came before the board in",
                "was then heard in", "were then heard in"]

    subset, keyword = find_closest_subset(text = case_content_str, keywords = keywords)

    if subset:
        subset = subset.replace(keyword, "")
        subset = subset.split()
        subset = [tok for tok in subset if tok not in ['in', 'on', 'via', 'together', 'by']]
        subset = " ".join(subset).strip()
        subset = subset.replace("With The Request To Review", "")

    if subset: # sometimes the hearing location is redacted and replaced with [CITY]
        if str(subset) != "[CITY]":
            return subset.title().replace("And Avenue, Unit 2 ", "").strip()

    # otherwise, go by postal code
    subset = get_ltb_location_by_postal_code(case_content_str = case_content_str)
    if subset:
        return subset.title().replace("And Avenue, Unit 2 ", "").strip()
    else:
        return None
    
for row in data_df.itertuples():

    try:
        location = get_ltb_location(data_df.loc[row.Index, 'content'])#.title() # returns the string in title case

        if location:
            data_df.at[row.Index, 'ltb_location'] = location
        else:
            data_df.at[row.Index, 'ltb_location'] = "LOCATION NOT FOUND"

    except Exception as any_error:
        data_df.at[row.Index, 'ltb_location'] = "LOCATION NOT FOUND"

def find_date(text: str):
    """
    Finds a date in the format "Month Day, Year" within the given text.

    Args:
        text (str): The input text to search for a date.

    Returns:
        str: The date found in the text. Returns an empty string if no date is found.

    Examples:
        >>> find_date("The event will take place on April 23, 2018.")
        "April 23, 2018"
    """

    pattern = r"\b[A-Z][a-z]+ \d{1,2}, \d{4}\b"
    match = re.search(pattern, text)

    if match:
        return match.group()
    else:
        return ""

def get_hearing_date(case_content_str: str):
    """
    Extracts the hearing date from the given case content string.

    Args:
        case_content_str (str): The case content string to extract the hearing date from.

    Returns:
        str or None: The extracted hearing date in the format "Month Day, Year" if found, otherwise None.

    Examples:
        >>> get_hearing_date("The application was heard on April 23, 2018. It is determined that...")
        "April 23, 2018"
    """

    for keyword in ["determinations:", "it is determined"]:
        if keyword in case_content_str.lower():
            kw_idx = case_content_str.find(keyword)
            break
        else:
            kw_idx = -1

    subset = case_content_str[case_content_str.lower().find("application") : kw_idx].strip()
    date = find_date(subset)

    if date:
        return date.strip()
        
    # otherwise return None
    return None

for row in data_df.itertuples():

    try:
        data_df.at[row.Index, 'hearing_date'] = get_hearing_date(data_df.loc[row.Index, 'content']) # is already a str
    except Exception as any_error:
        data_df.at[row.Index, 'hearing_date'] = "HEARING DATE NOT FOUND"

def find_date(text: str):
    """
    Finds a date in the format "Month Day, Year" within the given text.

    Args:
        text (str): The input text to search for a date.

    Returns:
        str: The date found in the text. Returns an empty string if no date is found.

    Examples:
        >>> find_date("The event will take place on April 23, 2018.")
        "April 23, 2018"
    """

    pattern = r"\b[A-Z][a-z]+ \d{1,2}, \d{4}\b"
    match = re.search(pattern, text)

    if match:
        return match.group()
    else:
        return ""

def extract_date(text, nlp = nlp):
    """
    Extracts a date from a string of text using spaCy's entity recognition.

    Args:
        text (str): The text to extract the date from.

    Returns:
        str: The extracted date string, or an empty string if no date is found.

    Examples:
        >>> extract_date("The event will take place on April 23, 2018.")
        "April 23, 2018"
    """

    doc = nlp(text)

    for entity in doc.ents:
        if entity.label_ == "DATE":
            return entity.text

    return ""

def convert_date(date_str):
    """
    Parses a date string in any format and converts it to the format "Month Day, Year".

    Args:
        date_str (str): The date string to parse.

    Returns:
        str: The parsed date string in the format "Month Day, Year", or an empty string if parsing fails.

    Examples:
        >>> convert_date("2022-05-31")
        "May 31, 2022"

        >>> convert_date("05/31/2018")
        "May 31, 2018"
    """

    try:
        parsed_date = parse(date_str)
        formatted_date = parsed_date.strftime("%B %d, %Y")
        return formatted_date
    except ValueError:
        return ""

def get_decision_date(case_content_str: str):
    """
    Extracts the decision date from the given case content string.

    Args:
        case_content_str (str): The case content string to extract the decision date from.

    Returns:
        str or None: The extracted decision date in the format "Month Day, Year" if found, otherwise None.

    Examples:
        >>> get_decision_date("The date order issued on April 23, 2018 states...")
        "April 23, 2018"
    """

    # intentionally searches these in this order. Any amendment would be the most recent date
    for keyword in ['date order amended', 'date issued', 'date order issued']: 
        if keyword in case_content_str.lower():
            di_idx = case_content_str.lower().find(keyword)
            subset = case_content_str[di_idx - 18 : di_idx].strip().split(". ")[-1]
            return subset.strip()
    
    else:
        if "date" in case_content_str.lower()[: 500]:
            subset = case_content_str[: 500]
            date_idx = case_content_str.lower().find('date')
            subset = case_content_str[date_idx + len('date') : date_idx + len('date') + 50].strip()
            subset = extract_date(subset).strip()
            return convert_date(subset).strip()
    
    # otherwise return None
    return None

for row in data_df.itertuples():

    try:
        data_df.at[row.Index, 'decision_date'] = get_decision_date(data_df.loc[row.Index, 'content']) # is already a str
    except Exception as any_error:
        data_df.at[row.Index, 'decision_date'] = "DECISION DATE NOT FOUND"

def get_url_from_citation_string(text: str):
    """
    Returns URL to case file given a list of strings of metadata from a case file.
    String must begin with "Citation: " and URL must be within angle brackets.

    Parameters
    ----------
    text : str
        A string of metadata from a case file.

    Returns
    -------
    str
        A string of the URL to the case file.
    """

    pattern = r"<(.*?)>"
    matches = re.findall(pattern, text)
    return matches[0]

def get_url_from_metadata(case_metadata: list):
    """
    Extract URL to case file from a list of strings of metadata from a case file.

    Parameters
    ----------
    case_metadata : list
        A list of strings of metadata from a case file.

    Returns
    -------
    str
        A string of the URL to the case file.
    """

    if isinstance(case_metadata, str):
        case_metadata = case_metadata.split("\n")

    for line in case_metadata:
        if ("Citation:" or "Référence:") in line:
            return get_url_from_citation_string(line)
        
    return None

for row in data_df.itertuples():

    try:
        data_df.at[row.Index, 'url'] = get_url_from_metadata(data_df.loc[row.Index, 'metadata'])
    except Exception as any_error:
        data_df.at[row.Index, 'url'] = "URL NOT FOUND"

def get_adj_member(case_content_str: str):
    """
    Retrieves the adjudicating member(s) mentioned in the given case content string.

    Args:
        case_content_str (str): The input string containing the case content.

    Returns:
        str: The adjudicating member(s) mentioned in the case content. If no adjudicating member is found, returns "nan".

    Examples:
        >>> get_adjudicating_member("This is the entire case file. There are sentences and other text.")
        "Name of Adjudicating Member"

    Notes:
        The function looks for specific keywords in the `case_content_str` to identify the adjudicating member(s).
        The keywords are evaluated in the following order: "date issued", "date of reasons", and "date order issued".
        If multiple instances of the same keyword are found, the function extracts the adjacent text and processes it to retrieve the member(s).
        If only one instance of the keyword is found, the function extracts the adjacent text and processes it to retrieve the member(s).
        If no adjudicating member is found, the function returns "nan".

    Raises:
        TypeError: If `case_content_str` is not a string.

    """

    keyword_1 = "date issued" # this is the most reliable one
    keyword_2 = "date of reasons" # first fallback
    keyword_3 = "date order issued" # second fallback

    # find which is best for the case (in order of best option to worst option)
    if keyword_1 in case_content_str.lower():
        keyword = keyword_1
        # kw_idx = case_content_str.lower().find(keyword_1)
    
    elif keyword_2 in case_content_str.lower():
        keyword = keyword_2
        # kw_idx = case_content_str.lower().find(keyword_2)

    elif keyword_3 in case_content_str.lower():
        keyword = keyword_3
        # kw_idx = case_content_str.lower().find(keyword_3)

    # if nothing is found, better to return nothing than to return something clearly incorrect
    if not keyword:
        return "nan"
    
    # getting index of whichever keyword was found first
    kw_idxs = find_all_positions(text = case_content_str.lower(), keyword = keyword)
    
    
    ### If there are multiple members found ###

    if len(kw_idxs) > 1:

        adj_membs = []

        for kw_idx in kw_idxs:
                
            subset = case_content_str[kw_idx + len(keyword): kw_idx + 100] # subsetting to an arbitrary distance after the keyword location
            subset = subset.split(", ")[0].strip()

            # removing "member" if applicable
            if "member" in subset.lower():
                memb_idx = subset.lower().find("member")
                subset = subset[: memb_idx].strip()

            # removing "vice chair" if applicable
            if "vice chair" in subset.lower():
                memb_idx = subset.lower().find("vice chair")
                subset = subset[: memb_idx].strip()

            # removing "vice chair" if applicable
            if "vice-chair" in subset.lower():
                memb_idx = subset.lower().find("vice-chair")
                subset = subset[: memb_idx].strip()

            # return subset
            adj_membs.append(subset)

        return ", ".join(list(set([memb for memb in adj_membs if memb != ""]))) # removing empty and duplicate items
    
    ### If there's only one member found ###

    kw_idx = case_content_str.lower().find(keyword)

    subset = case_content_str[kw_idx + len(keyword): kw_idx + 100] # subsetting to an arbitrary distance after the keyword location
    subset = subset.split(", ")[0].strip()

    # removing "member" if applicable
    if "member" in subset.lower():
        memb_idx = subset.lower().find("member")
        subset = subset[: memb_idx].strip()

    # removing "vice chair" if applicable
    if "vice chair" in subset.lower():
        memb_idx = subset.lower().find("vice chair")
        subset = subset[: memb_idx].strip()

    # removing "vice chair" if applicable
    if "vice-chair" in subset.lower():
        memb_idx = subset.lower().find("vice-chair")
        subset = subset[: memb_idx].strip()

    return subset

for row in data_df.itertuples():

    try:
        data_df.at[row.Index, 'adjudicating_member'] = get_adj_member(data_df.loc[row.Index, 'content']).replace("Vice Chair", "").replace("Vice-Chair", "").strip()
    except Exception as any_error:
        data_df.at[row.Index, 'adjudicating_member'] = "MEMBER NOT FOUND"

def find_all_positions(text: str, keyword: str):
    """
    Finds all positions of a keyword in a given text.

    This function searches for a keyword in a given text and returns a list of positions where the keyword is found.

    Parameters
    ----------
    text : str
        The text to search within.
    keyword : str
        The keyword to find in the text.

    Returns
    -------
    list
        A list of integers representing the positions of the keyword in the text.

    Examples
    --------
    >>> find_all_positions("This is an example sentence.", "example")
    [11]
    """
    positions = []
    start = 0
    while True:
        index = text.find(keyword, start)
        if index == -1:
            break
        positions.append(index)
        start = index + 1
    return positions

def get_outcome_span(text: str, return_truncated: bool = True):
    """
    Extracts the outcome span from a given text using different methods.

    This function extracts the outcome span from a given text using multiple methods. It first attempts to find
    the span between occurrences of the phrases "accordance with" and "ordered". If that method fails, it then
    tries to find the span after the phrase "it is ordered". If that also fails, it looks for the span after the
    phrase "find". The function returns the extracted outcome span as a cleaned string.

    Parameters
    ----------
    text : str
        The text from which to extract the outcome span.

    Returns
    -------
    str or None
        The extracted outcome span as a cleaned string, or None if no span is found.

    Examples
    --------
    >>> get_outcome_span(unstructured_case_file)
    "In accordance with the order, it is ordered that the defendant pays a fine."
    """

    ############### FIRST METHOD ################

    for keyword in ['in accordance with', 'grant', 'relief', 'fair']: # these all seem common but none seem to exist in 100% of cases

        if keyword in text:

            # find all occurrences of 'in accordance with' and 'ordered'
            accordance_with_indices = [m.end() for m in re.finditer(keyword, text)]
            ordered_indices = [m.start() for m in re.finditer("ordered", text)]

            # generate all possible pairs of indices
            index_pairs = list(itertools.product(accordance_with_indices, ordered_indices))

            # filter pairs where 'accordance with' index is less than 'ordered' index
            index_pairs = [(i, j) for (i, j) in index_pairs if i < j]
            if index_pairs:
                # find the pair with the shortest distance between indices
                min_distance_pair = min(index_pairs, key = lambda x: x[1] - x[0])
                try:
                    best_subset = text[min_distance_pair[0] - 300 : min_distance_pair[1] + 400].strip()
                except IndexError:
                    best_subset = text[min_distance_pair[0] - 600 : min_distance_pair[1]].strip()

                best_subset = best_subset.split(". ")

                if not best_subset:
                    continue # to next match of all matches of the keyword

                sent_id = [idx for idx, i in enumerate(best_subset) if keyword in i.lower()][0]

                clean_outcome = best_subset[sent_id]

                # return JUST the (presumably) most relevant outcome span (after cleaning it up a bit)
                if return_truncated:
                    clean_outcome = re.sub(r'\[\d+\]', '', clean_outcome)
                    clean_outcome = re.sub(r'^\d+\.\s*', '', clean_outcome).strip() # removes numbers from the start of the string such as "16. " from start of string

                    if ")" in clean_outcome[:10] and "(" not in clean_outcome[:10]:
                        clean_outcome = clean_outcome.split(")")[1].strip()
                    return clean_outcome

                # return all case file text until the end of the outcome span
                else:
                    return text[: text.find(clean_outcome) + len(clean_outcome)].strip()

    ################ SECOND METHOD ################

    keyword = "it is ordered"
    if keyword in text.lower():
        matches = find_all_positions(text.lower(), keyword)

        for match in matches:
            try: # match + 400 chars
                clean_outcome = ". ".join(text[match - 400 : match + 400].split(". ")[1:-1]) 
            except IndexError: # match idx until end of string (+ 400 is sometimes out of range)
                clean_outcome = ". ".join(text[match - 600 :].split(". ")[1:-1])

            # return None
            # print("METHOD 2")
            if not clean_outcome:
                continue # to next match of all matches of the keyword

            if return_truncated:
                clean_outcome = re.sub(r'\[\d+\]', '', clean_outcome)
                clean_outcome = re.sub(r'^\d+\.\s*', '', clean_outcome).strip() # removes numbers from the start of the string such as "16. " from start of string

                if ")" in clean_outcome[:10] and "(" not in clean_outcome[:10]:
                    clean_outcome = clean_outcome.split(")")[1].strip()
                return clean_outcome

            # return all case file text until the end of the outcome span
            else:
                return text[: text.find(clean_outcome) + len(clean_outcome)].strip()

    ############### THIRD METHOD ################

    keyword = " find " # spaces to prevent "finding" or other derivations from being included -- specifically looking for statements like "I find that..."
    if keyword in text.lower():
        matches = find_all_positions(text.lower(), keyword)
        for match in matches:

            try: # match + 400 chars
                clean_outcome = ". ".join(text[match - 400 : match + 400].split(". ")[1:-1]) 
            except IndexError: # match idx until end of string (+ 400 is sometimes out of range)
                clean_outcome = ". ".join(text[match - 600 :].split(". ")[1:-1])

            if not clean_outcome:
                continue # to next match of all matches of the keyword
            
            if return_truncated:
                clean_outcome = re.sub(r'\[\d+\]', '', clean_outcome)
                clean_outcome = re.sub(r'^\d+\.\s*', '', clean_outcome).strip() # removes numbers from the start of the string such as "16. " from start of string

                if ")" in clean_outcome[:10] and "(" not in clean_outcome[:10]:
                    clean_outcome = clean_outcome.split(")")[1].strip()
                return clean_outcome
            else:
                return text[: text.find(clean_outcome) + len(clean_outcome)].strip()

    # if absolutely nothing works, return none and try Longformer or something idk
    return None

for row in data_df.itertuples():

    try:
        pass
        content_str = data_df.at[row.Index, 'content']
        data_df.at[row.Index, 'outcome_span'] = get_outcome_span(content_str, return_truncated = True)
    except Exception as any_error:
        print(f"{any_error} with file at Df row: ", row.Index)

#################################### MODELS START ###################################

def q_prompt(raw_texts, q_lst, q_no):
    '''
    This function has some overlap with `general_cleaning` and `separate_file_sections`.
    It cleans the raw text and make it a prompt to feed in the LLMs.
    
    Parameters
    ----------
    raw_texts
        The raw file content as a pandas.core.series.Series, is a column of the target pandas dataframe.
    q_lst
        The list of question that will be predicted with a certain model
    q_no
        The index of the prompt in `q_lst`

    Returns
    -------
    list
        A list of cleaned prompts to be tokenized as inputs of the LLMs. 

    '''
    
    input_texts = []
    
    for i in range(len(raw_texts)):
        full_text = raw_texts[i]
       
        text = full_text[full_text.find('Content:')+len('Content:'):]

        text = text.replace('\n', ' ')
        text = text.replace('\xa0', ' ')
        text = text.replace('\t', ' ')
        text = text.replace('   ', ' ').replace('  ', ' ').replace('  ', ' ').replace('  ', ' ')
        
        if 'Schedule 1' in text:
            s_idx = text.find('Schedule 1')
            text = text[:s_idx]

        input_text = f'Question: {q_lst[q_no]} Text: {text}'  
        input_texts.append(input_text)

    return input_texts


def q_preprocess(raw_texts, q_lst, q_no, tokenizer):
    input_texts = q_prompt(raw_texts, q_lst, q_no)   
    
    input_toks = tokenizer.batch_encode_plus(input_texts,
                                             add_special_tokens=False, 
                                             return_token_type_ids=False)
    
    return input_toks
    

class CaseDataset(Dataset):

    def __init__(self, inputs):
        self.inputs = inputs

    def __len__(self):
        return len(self.inputs["input_ids"])

    def __getitem__(self, idx):
        input_ids = self.inputs['input_ids'][idx]
        attention_mask = self.inputs['attention_mask'][idx]
        return {"input_ids": input_ids, "attention_mask":attention_mask}

# The tokenizers are different for different models, so the padding_value would be different.
# Therefore, we use different collate functions
def collate_fn_led(batch):    # for LED model
    batch_input = [torch.LongTensor(example['input_ids']) for example in batch]
    batch_mask = [torch.LongTensor(example['attention_mask']) for example in batch]

    padded_batch_input_ids = pad_sequence(batch_input, batch_first=True, padding_value=led_tokenizer.pad_token_id)
    padded_batch_att_mask = pad_sequence(batch_mask, batch_first=True, padding_value=-100)

    return {"input_ids": padded_batch_input_ids, "attention_mask": padded_batch_att_mask}

def collate_fn_longt5(batch):    # for LongT5 model
    batch_input = [torch.LongTensor(example['input_ids']) for example in batch]
    batch_mask = [torch.LongTensor(example['attention_mask']) for example in batch]

    padded_batch_input_ids = pad_sequence(batch_input, batch_first=True, padding_value=longt5_tokenizer.pad_token_id)
    padded_batch_att_mask = pad_sequence(batch_mask, batch_first=True, padding_value=-100)

    return {"input_ids": padded_batch_input_ids, "attention_mask": padded_batch_att_mask}

def to_device(data, device):   
    new_data = {}
    for k in data:
        new_data[k] = data[k].to(device)
    return new_data


@torch.no_grad()
def answer(model, loader, tokenizer):
    all_preds = []
    all_labels = []
    model.eval()
    for batch in loader:
        batch = to_device(batch, device)
        input_ids = batch["input_ids"]
        attention_mask = batch["attention_mask"]
        outputs = model.generate(input_ids=input_ids, 
                                 attention_mask=attention_mask, 
                                 return_dict_in_generate=True, 
                                 pad_token_id=tokenizer.pad_token_id, 
                                 max_length=512, 
                                 top_k=15)
        
        decode_texts = tokenizer.batch_decode([l[l != 0] for l in outputs['sequences']])
        
        for decode in decode_texts:
            p = decode.replace('</s>', '').replace('<pad>','').replace('<s>', '')
            all_preds.append(p)
    
    return all_preds


def get_pred_dataloader(raw_texts, q_lst, q_no, tokenizer):
    input_toks = q_preprocess(raw_texts, q_lst, q_no, tokenizer)
    dataset = CaseDataset(input_toks)
    if tokenizer == led_tokenizer:
        dataloader = DataLoader(dataset, 
                                batch_size=64, 
                                collate_fn=collate_fn_led, 
                                shuffle=False)
    elif tokenizer == longt5_tokenizer:
        dataloader = DataLoader(dataset, 
                                batch_size=64, 
                                collate_fn=collate_fn_longt5, 
                                shuffle=False)
    # The batch sizes can be changed based on the GPU memory size
    # Generally speaking, batch size 64 is good for a GPU with 48G memory
    return dataloader


def answer_qs(raw_texts, q_lst, q_no, tokenizer, model):
    loader = get_pred_dataloader(raw_texts, q_lst, q_no, tokenizer)
    
    print(f'Q{q_no+1}: {q_lst[q_no]}') # to show the process
    preds = answer(model, loader, tokenizer)
    
    return preds

# Before running the codes below, please make sure you have downloaded the model checkpoints using the following quick urls:

# Longformer-Encoder-Decoder (LED) (3 epochs): https://huggingface.co/GraceQ/ltb_decision_led/tree/main
# Please download the led_3epoch_law_allqs.pt

# LongT5 (3 epochs): https://huggingface.co/GraceQ/ltb_decision_longt5/tree/main
# Please download the longT5_3epoch_law_allqs.pt

# The download info can also be found in model_download_urls.txt.


# @article{Beltagy2020Longformer,
#   title={Longformer: The Long-Document Transformer},
#   author={Iz Beltagy and Matthew E. Peters and Arman Cohan},
#   journal={arXiv:2004.05150},
#   year={2020},
# }
led_tokenizer = AutoTokenizer.from_pretrained("allenai/led-base-16384")
led3 = AutoModelForSeq2SeqLM.from_pretrained("allenai/led-base-16384", gradient_checkpointing=True, use_cache=False)
led3.load_state_dict(torch.load('led_3epoch_law_allqs.pt', map_location=device))


# @article{guo2021longt5,
#   title={LongT5: Efficient Text-To-Text Transformer for Long Sequences},
#   author={Guo, Mandy and Ainslie, Joshua and Uthus, David and Ontanon, Santiago and Ni, Jianmo and Sung, Yun-Hsuan and Yang, Yinfei},
#   journal={arXiv preprint arXiv:2112.07916},
#   year={2021}
# }
longt5_tokenizer = AutoTokenizer.from_pretrained("google/long-t5-local-base")
longt5 = AutoModelForSeq2SeqLM.from_pretrained("google/long-t5-local-base")
longt5.load_state_dict(torch.load('longT5_3epoch_law_allqs.pt', map_location=device))


raw_file_text = data_df['raw_file_str']

led3_qs = [
    'Did the decision state the landlord was represented?',
    'Did the tenant propose a payment plan?',
    'If the tenant did propose a payment plan, did the member accept the proposed payment plan?',
    'Did the decision state that the tenant had children living with them?',
    'Was the tenant employed at the time of the hearing?',
          ]

longt5_qs = [
    'Did the decision state the tenant was represented?',
    'If the tenant had a history of arrears, did the decision mention a history of the tenant making payments on those arrears (separate from any payments made in response to the present eviction notice/hearing)?',
    'If the tenant was not employed, did the decision state the tenant was receiving any form of government assistance (e.g. OW, childcare benefits, ODSP, OSAP)?',
    'If the tenant was employed, did the decision state any doubts about the stability of employment e.g. lack of guaranteed hours, contract work, etc.?',
    'Did the member find the tenant had sufficient income to pay rent?'
]

preds_dict = {}

led3.to(device)
for i in range(len(led3_qs)):
    preds_dict[led3_qs[i]] = answer_qs(
        raw_file_text, led3_qs, i, led_tokenizer, led3
    )

del led3
gc.collect()   # Save the GPU RAM


longt5.to(device)
for i in range(len(longt5_qs)):
    preds_dict[longt5_qs[i]] = answer_qs(
        raw_file_text, longt5_qs, i, longt5_tokenizer, longt5
    )

del longt5, led_tokenizer, longt5_tokenizer  
gc.collect()    # Save the GPU RAM


llm_df = pd.DataFrame(preds_dict)
for key in llm_df:
    data_df[key] = llm_df[key]

###################################### MODELS END ########################################

# create the directory if it doesn't already exist
directory_name = "pipeline_output"
if not os.path.exists(directory_name):
    os.makedirs(directory_name)

## write everything to CSV
data_df.to_csv(f"{directory_name}/extracted_info.csv", index = False)