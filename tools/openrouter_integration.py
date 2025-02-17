from openai import OpenAI
import os

def query_deepseek_r1(prompt: str) -> str:
    """Simplest working API call with fail-safe"""
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            timeout=10  # Fail fast
        )
        
        response = client.chat.completions.create(
            model="deepseek/deepseek-r1",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        return response.choices[0].message.content.strip('"“"')
    except Exception as e:
        print(f"API Error: {e}")
        return ""  # Return empty to keep CSV intact

# Example usage
if __name__ == "__main__":
    response = query_deepseek_r1(
        prompt="Create a outreach message for a AI company CEO looking for enterprise sales hires"
    )
    print(response) 