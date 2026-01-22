import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

def run_sanity_check():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # List of models to try in order of stability
    test_models = ["gemini-flash-latest", "gemini-1.5-flash", "gemini-2.5-flash"]
    
    for model_name in test_models:
        try:
            print(f"⏳ Testing {model_name}...")
            llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key)
            response = llm.invoke("Say 'System Ready'")
            print(f"✅ SUCCESS: {model_name} is active. Response: {response.content}")
            return model_name
        except Exception as e:
            print(f"❌ {model_name} failed.")
    
    print("\n🚨 All models failed. Please check your API Key and Billing status in AI Studio.")

if __name__ == "__main__":
    run_sanity_check()