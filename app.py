import os
import time
from flask import Flask, render_template, request
from dotenv import load_dotenv
from google import genai

# ==========================================
# Load Environment Variables
# ==========================================

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# ==========================================
# Flask App
# ==========================================

app = Flask(__name__)

# ==========================================
# Gemini Helper Function
# ==========================================

def ask_gemini(prompt):

    models = [
        "gemini-2.5-flash",
        "gemini-2.0-flash"
    ]

    for model in models:

        for attempt in range(3):

            try:

                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                if response.text:
                    return response.text

            except Exception as e:

                print(f"{model} Attempt {attempt+1}: {e}")

                if "503" in str(e):
                    time.sleep(5)
                    continue

                break

    return """
⚠️ AI सर्वर इस समय व्यस्त है।

कृपया 1-2 मिनट बाद पुनः प्रयास करें।
"""

# ==========================================
# Home Page
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# Hanuman Page
# ==========================================

@app.route("/hanuman")
def hanuman():
    return render_template("hanuman.html")


# ==========================================
# History Page
# ==========================================

@app.route("/history/<name>")
def history(name):

    prompt = f"""
{name} के बारे में हिन्दी में लगभग 350 शब्दों में विस्तार से बताइए।

इन बिंदुओं को शामिल करें:

1. परिचय
2. जन्म या अवतार
3. प्रमुख कार्य
4. धार्मिक महत्व
5. रोचक तथ्य

उत्तर केवल हिन्दी में दें।

Markdown बिल्कुल मत प्रयोग करें।
"""

    history = ask_gemini(prompt)

    return render_template(
        "history.html",
        name=name,
        history=history
    )


# ==========================================
# AI Chat
# ==========================================

@app.route("/chat", methods=["GET", "POST"])
def chat():

    answer = ""

    if request.method == "POST":

        question = request.form["question"]

        prompt = f"""
तुम एक हिन्दू धर्म विशेषज्ञ AI हो।

उपयोगकर्ता का प्रश्न:

{question}

उत्तर:

केवल हिन्दी में दो।

उत्तर स्पष्ट, सरल और सही होना चाहिए।

Markdown का प्रयोग मत करो।
"""

        answer = ask_gemini(prompt)

    return render_template(
        "chat.html",
        answer=answer
    )


# ==========================================
# Error Pages
# ==========================================

@app.errorhandler(404)
def page_not_found(error):
    return render_template(
        "error.html",
        message="पेज नहीं मिला।"
    ), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template(
        "error.html",
        message="सर्वर में समस्या आ गई है। कृपया बाद में पुनः प्रयास करें।"
    ), 500


# ==========================================
# Run
# ==========================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )