import sys
from lxml import etree

def extract_history(section):
    history = section.find('histories/history')
    if history is not None:
        enacted = "Enacted: " + history.text.strip() if history.text else ''
        modchap_element = history.find('modchap')
        if modchap_element is not None:
            modchap = modchap_element.text
            sess = modchap_element.get('sess', '')
            enacted += f" by Chapter {modchap}, {sess}"
        modyear = section.find('modyear')
        if modyear is not None:
            enacted += f" [Session: {modyear.text}]"
        return enacted
    return ''

def process_section(section, indent=0):
    output = []
    section_number = section.get('number', '').split('(')[0]  # Only take the base section for comparison
    catchline = section.find('catchline')
    if catchline is not None:
        output.append(f"{' ' * indent}Section: {section_number} - {catchline.text}")

    # Extracting history details
    history_detail = extract_history(section)
    if history_detail:
        output.append(f"{' ' * (indent + 2)}{history_detail}")

    for child in section:
        if child.tag == 'tab':
            continue
        elif child.tag == 'subsection':
            text = child.text.strip() if child.text else ''
            number = child.get('number', '')
            current_line = f"{' ' * (indent + 2)}{number}: {text}"
            
            # Collect all xrefs that are children of this subsection
            xrefs = child.findall('xref')
            for xref in xrefs:
                ref_number = xref.get('refnumber')
                # Check if the reference is from the same base section
                if ref_number.split('(')[0] == section_number:
                    short_ref = ref_number.split('(')[-1].split(')')[0]  # Extracting just the subsection number
                    if "Subsection" in text:
                        ref = f" {short_ref}[Ref: {ref_number}]"
                    else:
                        ref = f" Subsection {short_ref}[Ref: {ref_number}]"
                else:
                    ref = f" {ref_number}[Ref: {ref_number}]"
                current_line += ref
                
            output.append(current_line)
            
            # For nested subsections
            output.extend(process_section(child, indent + 4))
        else:
            continue  # Skip any other tags at this level

    return output


def process_section2(section, indent=0):
    output = []
    catchline = section.find('catchline')
    if catchline is not None:
        number = section.get('number', '')
        output.append(f"{' ' * indent}Section: {number} - {catchline.text}")

    # Extracting history details
    history_detail = extract_history(section)
    if history_detail:
        output.append(f"{' ' * (indent + 2)}{history_detail}")

    for child in section:
        if child.tag == 'tab':
            continue
        elif child.tag == 'subsection':
            text = child.text.strip() if child.text else ''
            number = child.get('number', '')
            output.append(f"{' ' * (indent + 2)}{number}: {text}")
            # For nested subsections
            output.extend(process_section(child, indent + 4))
        elif child.tag == 'xref':
            ref = f"[Ref: {child.get('refnumber')}]"
            if output:
                output[-1] += f" {ref}"
            else:
                output.append(ref)

    return output

def process_chapter(chapter, indent=0):
    output = []
    catchline = chapter.find('catchline')
    if catchline is not None:
        number = chapter.get('number', '')
        output.append(f"{' ' * indent}Chapter: {number} - {catchline.text}")
    
    for section in chapter.findall('section'):
        output.extend(process_section(section, indent + 2))
        
    return output

def process_title(title):
    output = []
    catchline = title.find('catchline')
    if catchline is not None:
        number = title.get('number', '')
        output.append(f"Title: {number} - {catchline.text}")
    
    for chapter in title.findall('chapter'):
        output.extend(process_chapter(chapter, 2))
        
    return output

def main(input_file):
    with open(input_file, 'r') as f:
        tree = etree.parse(f)

    # Generate .lst content
    lst_content = process_title(tree.getroot())

    # Derive the output filename from the input filename
    output_file = input_file.replace('.xml', '.lst')

    # Write to .lst file
    with open(output_file, 'w') as f:
        f.write('\n'.join(lst_content))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please provide an XML file as an argument.")
    else:
        main(sys.argv[1])