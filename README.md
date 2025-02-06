# ICD-10 LLM TreeSearch

A package to extract ICD-10 coding and other structured information from pathology reports. Currently in beta mode for bone marrow-related pathology.

## Setup Instructions

### Creating a Python Virtual Environment

1. **Create the virtual environment:**
   ```sh
   py -m venv .venv
   ```

2. **Activate the virtual environment:**
   - On Windows:
     ```sh
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```sh
     source .venv/bin/activate
     ```

3. **Install the required dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Install the package in editable mode:**
   ```sh
   pip install -e .
   ```

## Usage Instructions

### Running the ICD-10 Code Search Application

1. **Navigate to the `apps` directory:**
   ```sh
   cd apps
   ```

2. **Run the `icd10_app.py` application:**
   This app allows you to find all ICD-10 entries containing a given word. It can also show the lineage of a given code.
   ```sh
   streamlit run icd10_app.py
   ```

3. **Run the `icd10_llm_app.py` application:**
   This app lets you select an ICD-10 code and the report associated with that code. It then runs the report through the LLM tree search algorithm to find all possible ICD-10 code paths associated with that report. The model result can be viewed side-by-side next to the ground truth code path.
   ```sh
   streamlit run icd10_llm_app.py
   ```

### Using the `ReportGenerator` Class

The `ReportGenerator` class in `model.py` is used to generate pathology reports based on ICD-10 codes. `api_type` currently supports `openai` and `fireworks`.

1. **Import the class:**
   ```python
   from model import ReportGenerator
   ```

2. **Initialize the class:**
   ```python
   report_generator = ReportGenerator(prompt_path='path/to/pathology_report.txt', api_type='openai', model_name='gpt-4o', temperature=0.01)
   ```

3. **Generate a report:**
   ```python
   generated_report = report_generator.invoke('C83.12')
   ```

### Using the `TreeSearchCode` Class

The `TreeSearchCode` class in `treesearch.py` is used to perform a tree search for ICD-10 codes using an LLM model.

1. **Import the class:**
   ```python
   from treesearch import TreeSearchCode
   ```

2. **Initialize the class:**
   ```python
   tree_search = TreeSearchCode(prompt_path='path/to/pathology_report.txt', model_name='gpt-4o', temperature=0.01)
   ```

3. **Run the tree search:**
   ```python
   paths = tree_search.run_through_llm_allpaths()
   ```

### Using the `PathologyReportExtractor` Class

The `PathologyReportExtractor` class in `model.py` is used to extract structured information from pathology reports.

1. **Import the class:**
   ```python
   from model import PathologyReportExtractor
   ```

2. **Initialize the class:**
   ```python
   extractor = PathologyReportExtractor(model_name='gpt-4o', temperature=0.0)
   ```

3. **Extract information from a report:**
   ```python
   response_content = extractor.invoke('pathology report text')
   ```

### Example Notebooks

Several example notebooks are provided to demonstrate the usage of the code:

- `codes_preprocessing.ipynb`
- `generator_4o.ipynb`
- `generator_llama.ipynb`
- `result_paths_filtering.ipynb`
- `tagging.ipynb`

These notebooks can be run to see the code in action and understand how to use the various features. Ensure API keys are properly called/stored in the environment for the LLM calls to work (see the notebooks and apps).
