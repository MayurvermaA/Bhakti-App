import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
from google import genai

# Load .env
load_dotenv()

# Gemini Client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# Flask App
app = Flask(__name__)

# ==========================
# Home Page
# ==========================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/hanuman")
def hanuman():
    return render_template("hanuman.html")


# ==========================
# History Page
# ==========================
@app.route("/history/<name>")
def history(name):

    prompt = f"""
{name} के बारे में हिन्दी में 300-400 शब्दों में विस्तार से बताइए।

इसमें शामिल करें:

1. परिचय
2. जन्म या अवतार
3. प्रमुख कार्य
4. धार्मिक महत्व
5. रोचक तथ्य

उत्तर केवल हिन्दी में दें।
Markdown का प्रयोग मत करें।
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
        )

        history = response.text

    except Exception as e:
        history = f"Error : {e}"

    return render_template(
        "history.html",
        name=name,
        history=history
    )


# ==========================
# AI Chat Page
# ==========================
@app.route("/chat", methods=["GET", "POST"])
def chat():

    answer = ""

    if request.method == "POST":

        question = request.form["question"]

        prompt = f"""
तुम एक हिन्दू धर्म विशेषज्ञ AI हो।

प्रश्न:
{question}

उत्तर केवल हिन्दी में दो।

Markdown का प्रयोग मत करो।
"""

        try:

            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
            )

            answer = response.text

        except Exception as e:

            answer = f"Error : {e}"

    return render_template(
        "chat.html",
        answer=answer
    )


# ==========================
# Run App
# ==========================
if __name__ == "__main__":
    app.run(debug=True)