import os
import sqlite3
import requests

from flask import Flask, render_template, request
from dotenv import load_dotenv

# ==========================================
# Load Environment
# ==========================================

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

app = Flask(__name__)

# ==========================================
# Database
# ==========================================

def init_db():

    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history_cache(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            content TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ==========================================
# OpenRouter AI
# ==========================================
def ask_ai(prompt):

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Bhakti App"
    }

    payload = {
        "model": "openai/gpt-oss-20b:free",
        "messages": [
            {
                "role": "system",
                "content": "तुम हिन्दू धर्म विशेषज्ञ AI हो। हमेशा उत्तर केवल हिन्दी में दो। Markdown का प्रयोग मत करो।"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60
        )

        print("=" * 50)
        print("Status:", response.status_code)
        print(response.text)
        print("=" * 50)

        if response.status_code != 200:
            return f"API Error ({response.status_code})"

        result = response.json()
        return result["choices"][0]["message"]["content"]

    except Exception as e:
        print(e)
        return f"Error: {e}"


  
   
# ==========================================
# Home
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
# History
# ==========================================

@app.route("/history/<name>")
def history(name):

    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT content FROM history_cache WHERE name=?",
        (name,)
    )

    row = cursor.fetchone()

    conn.close()

    if row:

        return render_template(
            "history.html",
            name=name,
            history=row[0]
        )

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

    history = ask_ai(prompt)

    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO history_cache(name,content)
        VALUES(?,?)
        """,
        (name, history)
    )

    conn.commit()
    conn.close()

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

        question = request.form.get("question", "")

        if question.strip():

            prompt = f"""
तुम हिन्दू धर्म विशेषज्ञ AI हो।

उपयोगकर्ता का प्रश्न:

{question}

उत्तर केवल हिन्दी में दो।

उत्तर सरल, स्पष्ट और तथ्यात्मक होना चाहिए।

Markdown का प्रयोग मत करो।
"""

            answer = ask_ai(prompt)

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
        message="⚠️ पेज नहीं मिला।"
    ), 404


@app.errorhandler(500)
def internal_error(error):

    return render_template(
        "error.html",
        message="⚠️ सर्वर में समस्या आ गई है। कृपया बाद में पुनः प्रयास करें।"
    ), 500

# ==========================================
# Main
# ==========================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )