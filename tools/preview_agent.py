# AIDIVISION Core Agent System

📦 **Version:** `v1.2-dev`
🗓️ **Status:** Plugin validation, LangChain preview, GUI builder, Stripe delivery, and persona agents (Nyx/Kyuss) integrated

---

### 🔄 Replacing `preview_agent.py` with Flask Web Preview Server

```python
# tools/preview_agent.py
from flask import Flask, request, jsonify
import yaml
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os

app = Flask(__name__)

llm = ChatOpenAI(
    temperature=0.3,
    model_name="gpt-3.5-turbo",
    openai_api_key=os.environ.get("OPENAI_API_KEY")
)

@app.route("/preview", methods=["POST"])
def preview():
    data = request.json
    yaml_input = data.get("yaml")
    try:
        agent_config = yaml.safe_load(yaml_input)
        prompt_text = agent_config.get("system_prompt", "You are a helpful assistant.")
        template = PromptTemplate.from_template("Input: {input}\nOutput:")
        chain = LLMChain(llm=llm, prompt=template)
        result = chain.run({"input": "Describe your capabilities."})
        return jsonify({"response": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def health():
    return "AIDIVISION Preview API is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
```
