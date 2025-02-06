from treesearch import TreeSearchCode
import simple_icd_10_cm as cm
import streamlit as st
import os

if "OPENAI_API_KEY" not in os.environ: 
    os.environ['OPENAI_API_KEY'] = "openai-api-key"

# wrap the next function to cache
@st.cache_data
def get_all_codes():
    return cm.get_all_codes()

# Function to print the hierarchy for a given code
def print_hierarchy(code, container):
    container.write("Ground Truth Hierarchy:\n")    
    # Get ancestors (parent categories)
    ancestors = cm.get_ancestors(code)
    # Display hierarchy from top to bottom

    for ancestor in reversed(ancestors[:-1]):
        container.write(f"Parent: {ancestor} - {cm.get_description(ancestor)}\n")
        
    container.write(f"Code: {code} - {cm.get_description(code)}")   

report_directory_path = st.sidebar.text_input("Enter the directory path containing the reports")
report_txt_upload = st.sidebar.file_uploader("Upload the report file    ", type=["txt"])
code_txt_upload = st.sidebar.file_uploader("Upload a code file", type=["txt"])
show_hide_toggle = st.sidebar.checkbox("Show/Hide Pathology Report")
container = st.container()
container_left, container_right = container.columns(2)

# read the text file if it exists
if report_txt_upload is not None:
    filename = report_txt_upload.name
    pathology_report = report_txt_upload.read().decode("utf-8")
    if show_hide_toggle:
        container.markdown("# Pathology Report:")
        container.markdown(pathology_report)


# extract filename from uploaded file
if code_txt_upload is not None:
    code = code_txt_upload.read().decode("utf-8")

    show_hide_toggle_code = st.sidebar.checkbox("Show/Hide ICD-10 Code Hierarchy")
    if show_hide_toggle_code:
        print_hierarchy(code, container_left)   


class TreeSearchCodeST(TreeSearchCode):

    def run_through_llm_allpaths(self, container):
        def explore_paths(current_code, path):
            if not cm.get_children(current_code):
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
                    container.write(f'Current level: {new_code} - {cm.get_description(new_code)}')
                    # Recurse deeper
                    explore_paths(new_code, new_path)

        paths = []
        initial_code = '2'
        # We start with path = [initial_code]
        explore_paths(initial_code, [initial_code])

        
        path_strings = []
        for path in paths:
            path_str = " -> ".join(path)
            path_strings.append(path_str)

        return path_strings

# Run LLM button
if st.sidebar.button("Run LLM"):
    container_right.write('Estimated Hierarchy\n')
    
    tree_serach_instance = TreeSearchCodeST(os.path.join(report_directory_path,filename), model_name='gpt-4o', temperature= 0.01)
    path_strings = tree_serach_instance.run_through_llm_allpaths(container_right)
    with open(f"tempfile.txt", "w") as file:
        for path in path_strings:
            file.write(path + "\n")
    # open paths_2.txt and read the contents
    with open("tempfile.txt", 'r') as file:
        content = file.read()
        # delete the last line
        content = content[:-1]
    content_copy = content
    list_of_all_paths = content_copy.split("\n")
    for path_string in list_of_all_paths:
        path_list = path_string.split(" -> ")
        if not cm.get_children(path_list[-1]):
            for i in range(2, len(path_list)):
                target_text = " -> ".join(path_list[:i])+"\n"
                # remove the target_text from content_copy
                content_copy = content_copy.replace(target_text, "")


    container_right.write("\nAll plausible paths (length >= 2):")
    content_copy_split = content_copy.split("\n")
    for path in content_copy_split:
        container_right.write(path)







