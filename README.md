# eclipse

Welcome to eclipse.

![eclipse](/images/eclipse.png)

## Galaxy

  - [Galaxy](#galaxy)
  - [Acknowledgement](#acknowledgement)
  - [Why Eclipse?](#why-eclipse)
  - [Compatibility](#compatibility)
  - [System dependencies](#system-dependencies)
  - [Installation](#installation)
  - [Upgrading](#upgrading)
  - [Usage.](#usage)
  - [Usage as a Module](#usage-as-a-module)
  - [Understanding the Output](#understanding-the-output)


## Acknowledgement

**First i would like to thank the All-Mighty God who is the source of all knowledge, without Him, this would not be possible.**





## Why Eclipse?

In today's digital age, the confidentiality and privacy of information are paramount. Eclipse is designed to address the growing concerns surrounding sensitive data management. Unlike traditional methods, Eclipse is not limited to identifying explicitly defined sensitive information; it delves deeper, detecting any sentences that may hint at or contain sensitive information.

**Sensitive Information Detection**: Eclipse can process documents to identify not only explicit sensitive information but also sentences that suggest the presence of such data else where. This makes it a useful invaluable tool for preliminary reviews when you need to quickly identify potential sensitive content in your documents.

**Privacy Preservation**: With concerns about data privacy in the context of Large Language Models (LLMs), Eclipse offers a potential solution. Before you send your data to APIs hosting LLM(s), Eclipse can screen your documents to ensure no sensitive information is inadvertently exposed.

### Appropriate Use Cases for Eclipse:
**Preliminary Data Screening**: Eclipse is ideal for initial screenings where speed is essential. It helps users quickly identify potential sensitive information in large volumes of text.

**Data Privacy Checks**: Before sharing documents or data with external parties or services, Eclipse can serve as a first line of defense, alerting you to the presence of sensitive information.

### Limitations:
Eclipse is designed for rapid assessments and may not catch every instance of sensitive information. Therefore:

- Eclipse should not be used as the sole tool for tasks requiring exhaustive checks, such as legal document review, where missing sensitive information could have significant consequences.

- Consider using Eclipse alongside thorough manual reviews and other security measures, especially in situations where the complete removal of sensitive information is crucial.

## Compatibility

Eclipse has been extensively tested and optimized for Linux platforms. As of now, its functionality on Windows or macOS is not guaranteed, and it may not operate as expected.

## System dependencies

- Storage: A minimum of 20GB is required.

- RAM: A minimum of 16GB RAM memory is required

- Graphics Processing Unit (GPU): While not mandatory, having at least 8GB of GPU memory is recommended for optimal performance.


**PYPI based distribution requirement(s)**

- [Python3](https://www.python.org/downloads/)

- Python3 (3.10 or later)
- PyTorch (A machine learning library for Python)
- Transformers library by Hugging Face (Provides state-of-the-art machine learning techniques for natural language processing tasks)
- Requests library (Allows you to send HTTP requests using Python)
- Termcolor library (Enables colored printing in the terminal)
- Prompt Toolkit (Library for building powerful interactive command lines in Python)

To install the above dependencies:

```bash
pip install torch transformers requests termcolor prompt_toolkit
```


**PIP**:

```
pip install eclipse-ai
```

To run eclipse simply run this command:

```bash 
eclipse
``` 

For performing operations that require elevated privileges, consider installing via sudo:

```bash
sudo pip install eclipse-ai
```

Then run:

```bash
sudo eclipse
```

## Upgrading

For optimal performance and to ensure access to the most recent advancements, we consistently release updates and refinements to our models. eclipse will proactively inform you of any available updates to the package or the models upon each execution.

PIP:

```bash
pip install eclipse-ai --upgrade
```

## Usage.

``` bash
usage: eclipse [-h] [-p PROMPT] [-f FILE] [-m MODEL_PATH] [-o OUTPUT] [--debug] [-d DELIMITER] [-g] [-dir MODEL_DIRECTORY] [--line_by_line]

Entity recognition using BERT.

options:
  -h, --help            show this help message and exit
  -p PROMPT, --prompt PROMPT
                        Direct text prompt for recognizing entities.
  -f FILE, --file FILE  Path to a text file to read prompts from.
  -m MODEL_PATH, --model_path MODEL_PATH
                        Path to the pretrained BERT model.
  -o OUTPUT, --output OUTPUT
                        Path to the output HTML file.
  --debug               Enable debug mode to display label and confidence for every line.
  -d DELIMITER, --delimiter DELIMITER
                        Delimiter to separate text inputs, defaults to newline.
  -g, --use_gpu         Enable GPU usage for model inference.
  -dir MODEL_DIRECTORY, --model_directory MODEL_DIRECTORY
                        Directory where the BERT model should be downloaded and unzipped.
  --line_by_line        Process text line by line and yield results incrementally.
```

Here are some examples:

```bash
eclipse --prompt "Your text" --model_path path/to/your/model
eclipse --file input.txt --output path/to/your/output.html
```

Additional Options

```bash
--debug: Enables debug mode, providing more detailed output.
--delimiter: Specifies a custom delimiter for splitting input text into multiple lines (default is newline).
```

## Usage as a module

```python
# Correct import based on your project structure
from eclipse import process_text

model_path = "./ner_model_bert"
input_text = "Your example text here."

# Set this to True if you want to process the text line by line, or False to process all at once
line_by_line = False

try:
    # Handle both line-by-line processing and whole text processing
    if line_by_line:
        # Process the text line by line
        for result in process_text(input_text, model_path, "cpu", line_by_line=False):
            # In line-by-line mode, result should not be None, but check to be safe
            if result:
                (
                    processed_text,
                    highest_avg_label,
                    highest_avg_confidence,
                    is_high_confidence,
                ) = result
                print(f"Processed Text: {processed_text}")
                print(f"Highest Average Label: {highest_avg_label}")
                print(f"Highest Average Confidence: {highest_avg_confidence}")
                print(f"Is High Confidence: {is_high_confidence}")
            else:
                print("Error: Empty result for a line.")
    else:
        # Process the entire text as a single block
        result = process_text(input_text, model_path, "cpu", line_by_line=False)
        if result:
            (
                processed_text,
                highest_avg_label,
                highest_avg_confidence,
                is_high_confidence,
            ) = result
            print(f"Processed Text: {processed_text}")
            print(f"Highest Average Label: {highest_avg_label}")
            print(f"Highest Average Confidence: {highest_avg_confidence}")
            print(f"Is High Confidence: {is_high_confidence}")
        else:
            print("Error: Empty result for the text.")

except Exception as e:  # Catching general exceptions
    print(f"Error processing text: {e}")
```

## Understanding the Output
The script identifies entities in the text and classifies them into the following categories:

- O: No entity.
- NETWORK_INFORMATION: Information related to network addresses, protocols, etc.
- BENIGN: Text that is considered safe or irrelevant to security contexts.
- SECURITY_CREDENTIALS: Sensitive information like passwords, tokens, etc.
- PERSONAL_DATA: Personal identifiable information (PII) like names, addresses, etc.