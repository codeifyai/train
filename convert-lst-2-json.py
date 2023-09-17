import json

def process_lst_file(input_path, output_path):
    # Read the .lst file
    with open(input_path, 'r') as f:
        lines = f.readlines()
    
    # Process the lines to structure the data
    dataset = []
    current_section = ""
    for line in lines:
        if line.startswith("Section:"):
            if current_section:  # save the previous section if it exists
                dataset.append({'text': current_section})
            current_section = line.strip()  # start a new section
        else:
            current_section += " " + line.strip()
    
    if current_section:  # save the last section
        dataset.append({'text': current_section})
    
    # Save the processed dataset to a .json file
    with open(output_path, 'w') as f:
        json.dump(dataset, f, indent=4)
    
    return dataset

# Example Usage:
# process_lst_file('le.utah.gov_Title30.lst', 'processed_dataset.json')
