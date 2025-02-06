import simple_icd_10_cm as cm
import streamlit as st

# wrap the next function to cache
@st.cache_data
def get_all_codes():
    return cm.get_all_codes()

# In all_codes, find all codes that contain a specific word and the code has no children
def find_specific_codes(word):
    return [code for code in all_codes if word.lower() in cm.get_description(code).lower() and not cm.get_children(code)]

# Function to print the hierarchy for a given code


def print_hierarchy(code, container):
    # Get ancestors (parent categories)
    ancestors = cm.get_ancestors(code)
    # Display hierarchy from top to bottom
    for ancestor in reversed(ancestors):
        container.write(f"Parent: {ancestor} - {cm.get_description(ancestor)}\n")
        
    container.write(f"Code: {code} - {cm.get_description(code)}")

def find_main_ancestor(code):
    # print(f"\nCode: {code} - {cm.get_description(code)}")
    # Get ancestors (parent categories)
    ancestors = cm.get_ancestors(code)
    return ancestors[-1]

# Retrieve all ICD-10 codes
all_codes = cm.get_all_codes()



word_to_search = st.sidebar.text_input("Enter a word to search for codes")
if st.sidebar.button('Search'):
    specific_codes = find_specific_codes(word_to_search)
    for code in specific_codes:
        st.write(f"{code}: {cm.get_description(code)}")

# Display the hierarchy for a specific code
code_to_search = st.sidebar.text_input("Enter a code to search for its hierarchy")
if st.sidebar.button('Search Hierarchy'):
    print_hierarchy(code_to_search, st)



