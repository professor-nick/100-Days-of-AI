import os
import csv
import time
import random
from typing import Dict, List
import requests
from itertools import islice

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
API_KEY = os.getenv("OPENAI_API_KEY")  # Changed to OpenAI

class RateLimiter:
    def __init__(self, max_rpm: int = 3500, max_tpm: int = 90000):
        self.max_rpm = max_rpm
        self.max_tpm = max_tpm
        self.request_times = []
        self.token_counts = []

    def wait_if_needed(self):
        now = time.time()
        # Remove old entries
        self.request_times = [t for t in self.request_times if now - t < 60]
        self.token_counts = [t for t in self.token_counts if now - t < 60]
        
        # Check RPM limit
        while len(self.request_times) >= self.max_rpm:
            sleep_time = 60 - (now - self.request_times[0])
            print(f"RPM Limit: Waiting {sleep_time:.1f}s")
            time.sleep(sleep_time)
            now = time.time()
            self.request_times = [t for t in self.request_times if now - t < 60]
            
        # Check TPM limit
        while sum(self.token_counts) >= self.max_tpm:
            oldest = self.token_counts.pop(0)
            sleep_time = 60 - (now - self.request_times.pop(0))
            print(f"TPM Limit: Waiting {sleep_time:.1f}s")
            time.sleep(sleep_time)
            now = time.time()

    def record_usage(self, tokens_used: int):
        self.request_times.append(time.time())
        self.token_counts.append(tokens_used)

def generate_heygen_script(prompt: str, limiter: RateLimiter) -> str:
    """Generate HeyGen script using OpenAI API with rate limiting"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a professional comedy writer skilled in creating engaging video scripts."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    limiter.wait_if_needed()
    
    for attempt in range(5):
        try:
            response = requests.post(OPENAI_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            
            # Record usage
            tokens_used = response.json()['usage']['total_tokens']
            limiter.record_usage(tokens_used)
            
            return response.json()['choices'][0]['message']['content'].strip()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                retry_after = int(e.response.headers.get('Retry-After', 30)) 
                jitter = random.uniform(0.5, 1.5)
                wait_time = retry_after * jitter
                print(f"Rate limited. Waiting {wait_time:.1f}s (jittered)")
                time.sleep(wait_time)
                continue
            raise
        except Exception as e:
            print(f"Attempt {attempt+1}/5 failed: {str(e)}")
            if attempt < 4:
                time.sleep(2 ** attempt)
            else:
                return "ERROR: Script generation failed"

def process_csv(input_path: str, output_path: str = None, test_mode: bool = False):
    """Process CSV with enhanced rate limiting"""
    limiter = RateLimiter(max_rpm=2000, max_tpm=40000)  # Conservative limits
    
    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()
        
        rows = islice(reader, 10) if test_mode else reader
        
        for row in rows:
            if not row.get('Prompt for HeyGen Script'):
                print(f"Skipping {row.get('First Name', 'Unknown')}")
                writer.writerow(row)
                continue
                
            print(f"Processing {row.get('First Name', 'Unknown')}...")
            script = generate_heygen_script(row['Prompt for HeyGen Script'], limiter)
            row['HeyGen Script'] = script
            writer.writerow(row)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Process HeyGen prompts with OpenAI')
    parser.add_argument('input_csv', help='Path to input CSV file')
    parser.add_argument('--output', help='Optional output path')
    parser.add_argument('--test', action='store_true', help='Process first 10 entries only')
    args = parser.parse_args()
    
    process_csv(args.input_csv, args.output, args.test)
    print(f"Processing complete. Output saved to {args.output or args.input_csv.replace('.csv', '_processed.csv')}") 