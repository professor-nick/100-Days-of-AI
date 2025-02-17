import csv
import os
from openrouter_integration import query_deepseek_r1

def process_heygen_scripts():
    """Straightforward file-to-file processing"""
    input_file = "current deep work session/1-20 Complete Leads with HeyGen Script.csv"
    output_file = "current deep work session/1-20 Complete Leads with HeyGen Script_processed.csv"
    
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()
        
        for row in reader:
            if not row.get('HeyGen Script'):
                row['HeyGen Script'] = query_deepseek_r1(row['Prompt for HeyGen Script'])
            writer.writerow(row)
            print(f"Processed row {reader.line_num}")

if __name__ == "__main__":
    process_heygen_scripts() 