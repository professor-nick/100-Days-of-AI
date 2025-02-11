import pandas as pd
from collections import defaultdict

# Load datasets with proper encoding
apollo_df = pd.read_csv('lead_data/Get 1st AI Recruiting Client (USA, 70 Days, AI) - Apollo - Leads with Some Missing Funding Type.csv')
crunchbase_df = pd.read_csv('lead_data/Get 1st AI Recruiting Client (USA, 70 Days, AI) - Crunchbase - Leads with Correct Funding Type.csv')

# Clean company names for accurate matching
def clean_company_name(name):
    return str(name).lower().strip().replace(' ', '').replace('.','').replace('-','')

apollo_df['clean_name'] = apollo_df['Company Name'].apply(clean_company_name)
crunchbase_df['clean_name'] = crunchbase_df['Company Name'].apply(clean_company_name)

# Handle duplicates in Crunchbase data
print("Checking for duplicate company names in Crunchbase data...")
dupes = crunchbase_df[crunchbase_df.duplicated('clean_name', keep=False)]
if not dupes.empty:
    print(f"Found {len(dupes)} potential duplicates:")
    print(dupes[['Company Name', 'clean_name']])
    
    # Keep first occurrence and add suffix to others
    crunchbase_df = crunchbase_df.drop_duplicates(
        subset='clean_name', 
        keep='first'
    )
    print(f"Removed {len(dupes) - len(crunchbase_df)} duplicates")

# Create mapping for both funding type AND proper company name
name_funding_map = crunchbase_df.set_index('clean_name')[['Company Name', 'Funding Type']].to_dict(orient='index')

def get_correct_info(row):
    matches = []
    # First check exact match
    if row['clean_name'] in name_funding_map:
        matches.append(name_funding_map[row['clean_name']])
    
    # Then check partial matches
    for crunch_name, data in name_funding_map.items():
        if crunch_name in row['clean_name'] or row['clean_name'] in crunch_name:
            matches.append(data)
    
    # Take shortest company name match (avoids abbreviations)
    if matches:
        best_match = min(matches, key=lambda x: len(x['Company Name'])) 
        return best_match['Company Name'], best_match['Funding Type']
    
    return row['Company Name'], row['Funding Type']

# Apply corrections
apollo_df[['Corrected Company', 'Corrected Funding']] = apollo_df.apply(
    lambda x: get_correct_info(x), axis=1, result_type='expand'
)

# Create final DF with proper ordering
final_df = apollo_df[[
    'Corrected Company', 
    'Corrected Funding',
    'First Name',
    'LinkedIn URL',
    'Email'
]].rename(columns={
    'Corrected Company': 'Company Name',
    'Corrected Funding': 'Funding Type'
})

# Save the merged file
final_df.to_csv('lead_data/Apollo_Leads_Corrected_Funding.csv', index=False)

print(f"Merged file created with {len(final_df)} records")
print("Sample validation:")
print(final_df[['Company Name', 'Funding Type']].head(10)) 