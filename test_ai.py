from dotenv import load_dotenv
from google import genai

# 1. Load environment variables from the .env file
load_dotenv()

# 2. Initialize the Gemini client
# The SDK automatically looks for the GEMINI_API_KEY environment variable
client = genai.Client()

print("Sending request to Gemini... Please wait...")

try:
    # 3. Send a simple request to the gemini-2.5-flash model
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Hello Gemini! If you can hear me, please reply"
         " with a short sentence confirming everything is working fine.",
    )

    # 4. Print the AI's response
    print("\n--- Gemini Response ---")
    print(response.text)
    print("-----------------------")

except Exception as e:
    print(f"\n🛑 Connection Error: {e}")
