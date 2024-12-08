# OpenCoder Data Filtering Pipeline

## Overview

This repository presents the first heuristic filtering framework tailored to large-scale code pretraining corpus by considering the unique characteristics of different programming language, which contains over 100 filtering rules. Based on [RedPajamaV2](https://github.com/togethercomputer/RedPajama-Data), this framework extends and refines the existing rules from [StarCoder](https://github.com/bigcode-project/bigcode-dataset) to better align with the unique properties of code datasets, resulting in more precise and higher-quality data cleansing. 


## Features

- **Flexibility**
  - Separation of rule properties and rule thresholds. Different types of files can use specific sets of filtering rules or share the same rule properties with customized thresholds.
  - Thanks to the registration mechanism implemented using Python decorators (details in [base.py](./base.py)), the rules applied to different types of files can be easily reused in the same code implementation.
- **Extensibility**
  - In the [document.py](./document.py) file, we implemented a class specifically for loading code documents. This class can automatically compute and parse common attributes of code documents, making it easier to create new rules for the code documents.
  - This framework also supports custom implementations for filtering multiple other types of corpora (e.g., general text files, math-related files, etc.). By setting the parameter `spec` of the corresponding corpus rule registries, it is very easy to perform filtering process of multiple types of corpora within the same repository.
- **Transferability**
  - This framework is implemented as a class interface, making it very easy to migrate to various distributed systems such as **Hadoop**, **Spark**, **MaxCompute**, and others.
  

## Repository Structure

```markdown
📦 opc_data_filtering
├── 📂 artifacts                          (resource files)
├── 📂 examples
│   └── data_cleaning_example.ipynb       (an example of data filtering workflow)
├── 📂 pipeline
│   ├── code_filter_config.py             (configure of filtering thresholds)
│   ├── compute_filtering.py              (pipeline class for doing filtering process)
│   └── compute_quality_signals.py        (pipeline class for computing quality signals)
├── 📂 quality_signals                    (implementation of all the quality signals)
├── 📂 redpajama                          (copy from redpajama with a little modification)
├── 📂 test_data                          (test data used for the usage example)
├── 📂 utils    
├── base.py                               (implementation of quality signal register)
├── document.py                           (implementation of code document class)
├── README.md
└── requirements.txt

```

## Requirements
- Python version: `python>=3.7`
  
You can install the required packages with the following commands:
```bash
pip install -r requirements.txt
```
or
```bash
conda env create -f environment.yml
```

You also need to download our FastText model: [lang_predictor.bin](https://drive.google.com/file/d/1WFR0MgXWliRU4D0fCsb9OgjfPitNVaBD/view?usp=sharing), which is used to predict the language of each file, and put it into `./artifacts/`.

## Get Started
We have set up a simple data filtering workflow in [data_cleaning_example.ipynb](./examples/data_cleaning_example.ipynb), which processes the sample data in `./test_data/raw_code/` for users to use as a reference.


## Details of Filtering rules
### Categories
We developed the following three categories of filtering rules:

1. **Natural Language Filtering Rules**: These rules filter data based on common properties for all text files, such as file size, number of lines, and other general metrics. Both text and code files share these filtering rules.
2. **General Code Filtering Rules**: These rules apply to all code files by filtering data based on general code characteristics, such as the number of variables, average function length, and other common features.
3. **Language-Specific Filtering Rules**: These rules are designed according to the unique characteristics of specific programming languages, such as the frequency of “pass” statements in Python or the use of “goto” statements in C. We have developed these rules for the following eight commonly used programming languages: Python, C, C++, C#, Java, JavaScript, Go, and HTML.

### Filter Naming Rules
The name of filters will follow the following pattern: 

> **qsc\_[type]\_[metric]\_[unit]\_[description]**
- qsc: Code quality signal flag, which is fixed
- [type]: Category of quality signals, eg: doc, code, codec, codepython ...
- [metric]: Measurement metric, eg: num, frac, score, cate ...
- [unit]: Units used for statistics, eg: character, word, line ...
- [description]: Brief description of the quality signal
  

### How to add a new filtering rule?
Take the filter "qsc_code_num_chars" as an example:
1. Add an implementation of the quality signal in `./quality_signals/`. Please follow the filter naming rules.
```python
@register_quality_signal('qsc_code_num_chars', 'codedocument')
class QSC_Doc_Num_Chars(QSCodeBase):
    """
    The number of characters.
    """
    def __call__(self, document: QSCodeDocument) -> SignalType:
        return [(0, len(document), float(len(document)))]
```
2. Add the corresponding filtering thresholds into `./pipeline/code_filter_config.py`. Please consider that different type of files can set the specific thresholds.
```python
...
code_filter_config['others'] = {
  ...
  'qsc_code_num_chars': 'lambda x: x < 50',
  ...
}

code_filter_config['data'] = {
    ...
  'qsc_code_num_chars': 'lambda x: x < 50 or x > 5000',
  ...
}
...
```

<!-- ### Quality Signal Annotations
TODO -->