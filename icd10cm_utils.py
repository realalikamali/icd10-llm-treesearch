import simple_icd_10_cm as cm

# Function to print the hierarchy for a given code (only descriptions)
def get_hierarchy(code):
    description_string = ""
    # Get ancestors (parent categories)
    ancestors = cm.get_ancestors(code)
    # Display hierarchy from top to bottom
    for ancestor in reversed(ancestors):
        description_string += f"Parent: {cm.get_description(ancestor)}\n"
        
    description_string += f"Target Code Description: {cm.get_description(code)}"
    return description_string

# Function to print the hierarchy for a given code (code and descriptions)
def get_hierarchy_with_code(code):
    description_string = ""
    # Get ancestors (parent categories)
    ancestors = cm.get_ancestors(code)
    # Display hierarchy from top to bottom
    for ancestor in reversed(ancestors):
        description_string += f"Parent: {ancestor} - {cm.get_description(ancestor)}\n"
        
    description_string += f"Code: {code} - {cm.get_description(code)}"
    return description_string

def find_main_ancestor(code):
    # Get ancestors (parent categories)
    ancestors = cm.get_ancestors(code)
    return ancestors[-1]

def trim_path(path_file):
    # Remove duplicate paths from the paths.txt file
    # open paths.txt and read the original_pathss
    with open(path_file, 'r') as file:
        original_paths = file.read()
        # delete the last line ('\n)
        original_paths = original_paths[:-1]

    trimmed_paths = original_paths
    list_of_all_paths = original_paths.split("\n")
    for path_string in list_of_all_paths:
        path_list = path_string.split(" -> ")
        if not cm.get_children(path_list[-1]):
            for i in range(2, len(path_list)):
                target_text = " -> ".join(path_list[:i])+"\n"
                # remove the target_text from trimmed_paths
                trimmed_paths = trimmed_paths.replace(target_text, "")
    return trimmed_paths