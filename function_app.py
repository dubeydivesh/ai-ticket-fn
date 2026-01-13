import json
import os
import azure.functions as func
from openai import AzureOpenAI

app = func.FunctionApp()

@app.function_name(name="raiseazureticket")
@app.route(route="raiseazureticket", auth_level=func.AuthLevel.FUNCTION)
def raiseazureticket(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
        user_input = body.get("message")

        if not user_input:
            return func.HttpResponse(
                "Missing 'message' in request body",
                status_code=400
            )

        client = AzureOpenAI(
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_version="2024-12-01-preview"
        )

        prompt = f"""
You are an Azure Cloud Support expert.
Convert the following issue into a professional Azure support ticket.

Issue:
{user_input}

Return output in JSON with:
service, severity, environment, business_impact, description
"""

        response = client.chat.completions.create(
            model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
            messages=[
                {"role": "system", "content": "You generate Azure support tickets."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        ticket_text = response.choices[0].message.content.strip()

# IMPORTANT: convert string → dict
ticket_json = json.loads(ticket_text)

return func.HttpResponse(
    json.dumps({
        "ticket": ticket_json
    }),
    mimetype="application/json",
    status_code=200
)

        

    except Exception as e:
        return func.HttpResponse(
            str(e),
            status_code=500
        )
