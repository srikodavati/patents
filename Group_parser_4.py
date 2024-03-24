from bs4 import BeautifulSoup
import csv
import os 
import json 

def split_xml_documents(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    parts = content.split('<?xml version="1.0" encoding="UTF-8"?>')
    parts = [part for part in parts if part.strip()]
    xml_documents = ['<?xml version="1.0" encoding="UTF-8"?>' + part for part in parts]
    return xml_documents


def parse_xml_and_extract_data_bs(xml_documents):
    extracted_data = []
    for doc in xml_documents:
        soup = BeautifulSoup(doc, 'lxml-xml')
        doc_number = soup.find('doc-number').get_text() if soup.find('doc-number') else 'N/A'
        country = soup.find('country').get_text() if soup.find('country') else 'N/A'
        invention_title = soup.find('invention-title').get_text() if soup.find('invention-title') else 'N/A'
        date_publ = soup.find('us-patent-grant')['date-publ'] if soup.find('us-patent-grant') else 'N/A'
        status = soup.find('us-patent-grant')['status'] if soup.find('us-patent-grant') else 'N/A'
        abstract = ''
        if soup.find('abstract'):
            paragraphs = soup.find('abstract').find_all('p')
            abstract = ' '.join(p.get_text(separator=" ", strip=True) for p in paragraphs)

        us_citations = []
        for citation in soup.find_all('us-citation'):
            category = citation.find('category').get_text(strip=True) if citation.find('category') else ''
            if category == "cited by applicant":
                patcit = citation.find('patcit')
                if patcit:
                    document_id = patcit.find('document-id')
                    if document_id:
                        citation_data = {
                            'country': document_id.find('country').get_text(strip=True) if document_id.find('country') else 'N/A',
                            'doc_number': document_id.find('doc-number').get_text(strip=True) if document_id.find('doc-number') else 'N/A',
                            'kind': document_id.find('kind').get_text(strip=True) if document_id.find('kind') else 'N/A',
                            'date': document_id.find('date').get_text(strip=True) if document_id.find('date') else 'N/A',
                        }
                        us_citations.append(citation_data)

                        
        first_assignee = soup.find('assignee')
        assignee_orgname = first_assignee.find('orgname').get_text() if first_assignee and first_assignee.find('orgname') else 'N/A'
        assignee_address = first_assignee.find('address') if first_assignee else None
        assignee_country = assignee_address.find('country').get_text() if assignee_address and assignee_address.find('country') else 'N/A'
        assignee_state = assignee_address.find('state').get_text() if assignee_address and assignee_address.find('state') else 'N/A'
        
        inventors = soup.find_all('inventor')
        for inv in inventors:
            inventor_data = {}
            inventor_data['doc_number'] = doc_number
            inventor_data['country'] = country
            inventor_data['invention_title'] = invention_title
            inventor_data['date_published'] = date_publ
            inventor_data['status'] = status
            inventor_data['abstract'] = abstract 
            first_name = inv.find('first-name').get_text() if inv.find('first-name') else ''
            last_name = inv.find('last-name').get_text() if inv.find('last-name') else ''
            inventor_data['inventor_name'] = f"{first_name} {last_name}".strip()
            address = inv.find('address')
            inventor_data['inventor_country'] = address.find('country').get_text() if address and address.find('country') else 'N/A'
            inventor_data['inventor_state'] = address.find('state').get_text() if address and address.find('state') else 'N/A'
            inventor_data['assignee_orgname'] = assignee_orgname
            inventor_data['assignee_country'] = assignee_country
            inventor_data['us_citations'] = json.dumps(us_citations)
            inventor_data['assignee_state'] = assignee_state

            extracted_data.append(inventor_data)


        
    return extracted_data

def save_data_to_csv(data, csv_file_path):
    if not data:
        return
    
    # Determine all possible fieldnames
    fieldnames = set()
    for row in data:
        for key in row.keys():
            fieldnames.add(key)
    fieldnames = sorted(list(fieldnames))  # Sorting to ensure consistent column order
    
    with open(csv_file_path, 'w', newline='', encoding='utf-8', errors='replace') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)




def process_xml_files_in_directory(directory_path, output_csv_file):
    all_extracted_data = []
    for filename in os.listdir(directory_path):
        if filename.endswith('.xml'):
            file_path = os.path.join(directory_path, filename)
            xml_documents = split_xml_documents(file_path)
            extracted_data = parse_xml_and_extract_data_bs(xml_documents)
            all_extracted_data.extend(extracted_data)
    save_data_to_csv(all_extracted_data, output_csv_file)
    print(f"Data from all XML files extracted and saved to {output_csv_file}")


directory_path = '/Users/srilekhakodavati/Desktop/Patents/2023/4'
output_csv_file = '/Users/srilekhakodavati/Desktop/Patents/files/23_4.csv'

# Process all XML files in the specified directory
process_xml_files_in_directory(directory_path, output_csv_file)
