from model import CodeExtractorYesNo
import simple_icd_10_cm as cm



class TreeSearchCode:
    def __init__(self, prompt_path, model_name='gpt-4o', temperature= 0.01):
        self.extractor = CodeExtractorYesNo(prompt_path, model_name=model_name, temperature= 0.01)

    def output_parser(self, llm_output):
        """
        This method parses the output from the LLM model and returns a dictionary with keys 
        being the descriptions and values being Boolean True or False based on the Yes or No
        """
        estimation_dict = {}
        for line in llm_output.split("\n"):
            if line:
                try:
                    description, answer = line.split(":")
                    estimation_dict[description] = True if answer.strip() == "Yes" else False
                except ValueError:
                    raise ValueError(f"Line '{line}' is not in the expected 'description: answer' format.")
        return estimation_dict

    def create_children_description(self, root_code):

        """
        This method creates children nodes for the given code
        """
        # list of codes at a specific level
        children = cm.get_children(root_code)
        description_to_code_dict = {}
        code_descriptions_text = ""

        start_index = 2 if root_code == '2' else 0 # Remove the irrelevant codes from the '2' level
        for code in children[start_index:]:
            description_to_code_dict[cm.get_description(code)] = code
            code_descriptions_text += f"{cm.get_description(code)}" + "\n"
        return code_descriptions_text, description_to_code_dict
    

    def run_through_llm_allpaths(self):
        def explore_paths(current_code, path):
            if not cm.get_children(current_code):
                # paths.append(path)
                # print('\n')
                return
            
            code_descriptions_text, description_to_code_dict = self.create_children_description(current_code)
            output_dict = self.output_parser(self.extractor.invoke(code_descriptions_text))

            for desc, is_yes in output_dict.items():
                if is_yes:
                    new_code = description_to_code_dict[desc]
                    new_path = path + [new_code]
                    # Store the path if it has length >= 2
                    if len(new_path) >= 2:
                        paths.append(new_path)
                    print(f'Current level: {new_code} - Description: {cm.get_description(new_code)}')
                    # Recurse deeper
                    explore_paths(new_code, new_path)

        paths = []
        initial_code = '2'
        # We start with path = [initial_code]
        explore_paths(initial_code, [initial_code])

        print("\nAll plausible paths (length >= 2):")
        path_strings = []
        for path in paths:
            path_str = " -> ".join(path)
            print(path_str)
            path_strings.append(path_str)

        return path_strings
            