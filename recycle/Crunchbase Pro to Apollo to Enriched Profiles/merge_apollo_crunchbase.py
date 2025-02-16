import pandas as pd
from pathlib import Path
import urllib.parse
import argparse

def clean_domain(url):
    """Extract standardized domain from URL"""
    if pd.isna(url) or url.strip() == "":
        return ""
    
    try:
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc if parsed.netloc else parsed.path.split('/')[0]
        
        # Remove www and protocol prefixes
        domain = domain.lower().replace("www.", "").replace("http://", "").replace("https://", "")
        
        # Handle special cases and subdomains
        parts = domain.split('.')
        if len(parts) > 2:
            # Preserve .co.uk/.com.au type domains while removing subdomains
            tld_combos = ['.co.', '.com.', '.org.', '.net.', '.gov.']  # Add more as needed
            if any(f".{parts[-3]}." in combo for combo in tld_combos):
                return '.'.join(parts[-3:])  # Preserve 3-part domains like 'co.uk'
            return '.'.join(parts[-2:])  # Main domain + TLD
        return domain
    except Exception as e:
        print(f"Error cleaning domain {url}: {str(e)}")
        return url.lower().strip()

def generate_template(input_path):
    """Create template file with proper column structure"""
    template_path = input_path.replace(" Scraped by APIFY", " Enriched by Crunchbase Pro (TEMPLATE)")
    template_df = pd.read_csv(input_path, nrows=0)  # Get headers only
    
    # Add Crunchbase columns
    crunchbase_cols = [
        'Company Name', 'Last Funding Type', 'City', 'Description',
        'Full Description', 'Category 1', 'Category 2', 'Category 3',
        'Last Funded Date', 'CB Rank'
    ]
    
    for col in crunchbase_cols:
        if col not in template_df.columns:
            template_df[col] = None
    
    template_df.to_csv(template_path, index=False)
    print(f"Created template file at: {template_path}")

def merge_apollo_with_crunchbase(apollo_file, crunchbase_file, output_file):
    """Merge any Apollo file with master Crunchbase dataset"""
    # Read datasets
    apollo_df = pd.read_csv(apollo_file, keep_default_na=False)
    crunchbase_df = pd.read_csv(crunchbase_file, keep_default_na=False)
    
    # Clean domains
    apollo_df['clean_domain'] = apollo_df['Domain'].apply(clean_domain)
    crunchbase_df['clean_domain'] = crunchbase_df['Domain'].apply(clean_domain)
    
    # Merge datasets
    merged = apollo_df.merge(
        crunchbase_df[[
            'clean_domain', 'Company Name', 'Last Funding Type',
            'City', 'Description', 'Full Description', 'Category 1',
            'Category 2', 'Category 3', 'Last Funded Date', 'CB Rank'
        ]],
        on='clean_domain',
        how='left'
    )
    
    # Generate template for missing entries
    missing_domains = merged[merged['Company Name'].isna()]['Domain'].unique()
    if len(missing_domains) > 0:
        generate_template(apollo_file)
        print(f"⚠️  Found {len(missing_domains)} domains without Crunchbase matches")
        print("Template file created for manual data collection")

    # Final column order and save
    final_columns = [
        'Domain', 'LinkedIn Company URL', 'Twitter URL',
        'First Name', 'Job Title', 'Headline', 'Email',
        'LinkedIn URL', 'Industry', 'Phone',
        'Company Name', 'Last Funding Type', 'City',
        'Description', 'Full Description', 'Category 1',
        'Category 2', 'Category 3', 'Last Funded Date', 'CB Rank'
    ]
    
    merged[final_columns].to_csv(output_file, index=False)
    print(f"✅ Successfully created enriched file: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Merge Apollo data with Crunchbase master dataset')
    parser.add_argument('--apollo', required=True, 
        help='Input Apollo CSV filename e.g. "51-100 Apollo Scraped by APIFY.csv"')
    parser.add_argument('--crunchbase', required=True,
        help='Master Crunchbase CSV filename e.g. "Crunchbase Pro Scraped by APIFY.csv"')
    parser.add_argument('--output', 
        help='Output filename (default: auto-generated from Apollo name)')
    
    args = parser.parse_args()
    
    # Auto-generate output filename if not specified
    if not args.output:
        output_path = Path(args.apollo).name.replace(" Scraped by APIFY", " Enriched by Crunchbase Pro")
        args.output = f"current deep work session/{output_path}"
    
    merge_apollo_with_crunchbase(
        apollo_file=args.apollo,
        crunchbase_file=args.crunchbase,
        output_file=args.output
    ) 