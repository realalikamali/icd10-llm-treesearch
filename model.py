# %%
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_fireworks import ChatFireworks
from pydantic import BaseModel, Field

class CodeExtractorYesNo:
    def __init__(self, prompt_path, model_name='gpt-4o', temperature= 0.2):

        self.model_name = model_name
        self.temperature = temperature
        self.prompt_path = prompt_path
        self.model = self._initialize_model()
        # Load the pathology report text once at initialization
        with open(self.prompt_path, 'r') as file:
            self.pathology_report = file.read()

    def _initialize_model(self):
        model = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
        )
        return model


    def invoke(self, input_code_possibilities_only_descriptions: str):
        """
        Build the final prompt dynamically using:
          - A fixed instruction block (pre_prompt)
          - The loaded pathology report (self.pathology_report)
          - The user-supplied code descriptions (input_code_possibilities_only_descriptions)
        Then invoke the chain and return its output.
        """

        # Instruction block
        pre_prompt = (
            "Think carefully and tag the text as instructed: "
            "You are assuming the role of a medical coder. You are given a bone marrow pathology report and "
            "will use the ICD-10 guidelines to find the code corresponding to the report. You will do this task in "
            "steps. The ICD-10 has a hierarchy starting from major categories branching into chapters and "
            "smaller subcategories and subtypes. Consider each of the following ICD-10 code descriptions and "
            "evaluate if there are any related to the pathology report. "
            "In your response in each line, print the description followed by a : and a Yes or No."
            "If none of the descriptions match the report, it is okay to say No to all."
        )

        # Combine everything into one prompt string
        prompt_text = (
            f"{pre_prompt}\n\n"
            f"{self.pathology_report}\n\n"
            f"Code descriptions:\n{input_code_possibilities_only_descriptions}"
        )

        # Create a ChatPromptTemplate from the combined text
        chat_prompt = ChatPromptTemplate.from_template(template=prompt_text)
        
        # Build a chain (using the '|' operator to compose Runnables)
        chain = chat_prompt | self.model | StrOutputParser()

        # Invoke the chain. Since we didn't define any placeholders in the prompt,
        # we can call invoke with an empty dictionary.
        result = chain.invoke({})
        return result

class ReportGenerator:
    def __init__(self, prompt_path, api_type='openai', model_name='gpt-4o', temperature= 0.01):
        """
        Constructor for the ReportGenerator class.
        Initializes the model and loads the template pathology report.

        Inputs:
        prompt_path (str): Path to the template pathology report.
        api_type (str): 'openai' or 'fireworks'
        model_name (str): Name of the model to use.
        temperature (float): Temperature parameter for the model.
        """

        self.model_name = model_name
        self.temperature = temperature
        self.prompt_path = prompt_path
        self.api_type = api_type

        self.model = self._initialize_model()
        # Load the pathology report text once at initialization
        with open(self.prompt_path, 'r') as file:
            self.pathology_report = file.read()

    def _initialize_model(self):
        if self.api_type == 'openai':
            model = ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=1000
            )
        elif self.api_type == 'fireworks':
            model = ChatFireworks(
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=1000
            )

        return model


    def invoke(self, icd10_code: str):
        """
        Build the final prompt dynamically using:
          - A fixed instruction block (pre_prompt)
          - The template pathology report (self.pathology_report)
          - The user-supplied code hierarchy description
        Then invoke the chain and return its output.
        """

        # Instruction block
        pre_prompt = (
            "Using this bone marrow pathology template (and your own knowledge assuming you are a pathologist), "
            "and the provided hierarchy of ICD-10 coding, create a mock report corresponding to said coding. "
            "The report should corroborate the target ICD-10 code description. THE CODE ITSELF SHOULD NOT APPEAR IN THE REPORT, as coding is delegated to someone else. "
            "No need to replicate every specific detail from the template. For example, if a result is pending in the template, "
            "that doesn't need to necessarily be pending in the mock report."
            "The template is just a structure. So the you to modify the template's sections to include findings that would lead to the provided icd-10 code."
            "Your response should only be the report. Nothing before or after the report."
        )

        # Combine everything into one prompt string
        prompt_text = (
            f"{pre_prompt}\n\n"
            f"The template:\n\n{self.pathology_report}\n\n"
            f"The ICD-10 Code Hierarchy:\n{icd10_code}"
        )

        # Create a ChatPromptTemplate from the combined text
        chat_prompt = ChatPromptTemplate.from_template(template=prompt_text)
        
        # Build a chain (using the '|' operator to compose Runnables)
        chain = chat_prompt | self.model | StrOutputParser()

        # Invoke the chain. Since we didn't define any placeholders in the prompt,
        # we can call invoke with an empty dictionary.
        result = chain.invoke({})
        return result

# 1. Define pydantic model for structured output
class PathologyExtraction(BaseModel):
    presentation: str = Field(description="One of: 'first presentation', 'relapse', 'minimum residual disease', or 'other'.")
    disease_on_aspirate: str = Field(description="Yes, No, or Inconclusive")
    disease_on_peripheral_blood: str = Field(description="Yes, No, or Inconclusive")

class PathologyReportExtractor:
    def __init__(self, model_name='gpt-4o', temperature=0.0):
        """
        Constructor for the PathologyReportExtractor class.
        Initializes the model.

        Inputs:
        model_name (str): Name of the model to use.
        temperature (float): Temperature parameter for the model.
        api_key (str): API key for the model.
        """
        self.model_name = model_name
        self.temperature = temperature
        self.model = self._initialize_model()

    def _initialize_model(self):
        model = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
        ).with_structured_output(PathologyExtraction)
        return model

    def invoke(self, report: str):
        """
        Build the final prompt dynamically using:
          - A fixed instruction block (pre_prompt)
          - The user-supplied pathology report
        Then invoke the chain and return its output.
        """
        # Instruction block
        prompt_template = ChatPromptTemplate.from_template("""You will be given a pathology report. Extract the following information:
        1. Presentation: Choose from ['first presentation', 'relapse', 'minimum residual disease', 'other'].
        2. Disease on aspirate smear: 'Yes', 'No', or 'Inconclusive'.
        3. Disease on peripheral blood: 'Yes', 'No', or 'Inconclusive'.

        Here is the pathology report:

        ---
        {report}
        ---
        """)

        # Build a chain (using the '|' operator to compose Runnables)
        tagging_chain = prompt_template | self.model

        # Invoke the chain with the provided report
        response_content = tagging_chain.invoke({"report": report})
        return response_content