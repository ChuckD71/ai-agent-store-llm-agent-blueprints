# tools/preview_agent.py
from flask import Flask, request, jsonify, redirect
import yaml
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
import stripe

app = Flask(__name__)

# Stripe config
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
YOUR_DOMAIN = os.environ.get("DOMAIN", "https://ai-agent-store-llm-agent-blueprints.onrender.com")

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

@app.route("/buy", methods=["GET"])
def buy():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Blueprint Preview Access',
                    },
                    'unit_amount': 500,  # $5.00
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=YOUR_DOMAIN + '/?success=true',
            cancel_url=YOUR_DOMAIN + '/?canceled=true',
        )
        return redirect(session.url, code=303)
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    event = None
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # ✅ Here you could mark user/session as paid
        print(f"Payment succeeded: {session['id']}")
    return jsonify(success=True)

@app.route("/")
def health():
    return "AIDIVISION Preview API is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
