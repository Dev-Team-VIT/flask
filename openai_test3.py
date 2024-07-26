from flask import Flask, request, jsonify
import json
import matplotlib.pyplot as plt
from openai import AzureOpenAI

app = Flask(__name__)

# Azure OpenAI settings
api_key = "2142e2507c494b74999fb3bb680aca1e"
azure_endpoint = "https://testingbot2.openai.azure.com/"
api_version = "2024-05-01-preview"
assistant_id = "asst_Kqsj55EX0tMi1rQsp8PNY0wm"

# Create an Azure OpenAI client
client = AzureOpenAI(
    api_key=api_key,
    azure_endpoint=azure_endpoint,
    api_version=api_version,
)

@app.route('/investment_advice', methods=['POST'])
def investment_advice():
    data = request.get_json()
    investment_type = data['investment_type']
    annual_income = data['annual_income']
    num_fds = int(data['num_fds'])
    fd_amounts = data['fd_amounts']
    mutual_fund_investment = data['mutual_fund_investment']
    investment_options_type = data['investment_options_type']

    try:
        thread = client.beta.threads.create()
    except Exception as e:
        return jsonify({'error': f'Error creating thread: {e}'}), 500

    try:
        message_content = (
    f"I am seeking {investment_type} investment advice based on my current financial situation. "
    f"Here are the details:\n"
    f"Annual Income: ₹{annual_income}\n"
    f"Fixed Deposits (FDs): {num_fds} FDs of ₹{fd_amounts}\n"
    f"Mutual Funds: Investment of ₹{mutual_fund_investment}\n"
    f"Given this financial status, could you suggest some suitable {investment_options_type} investment options "
    f"that can help me diversify my portfolio and achieve high returns?\n"
    "Provide me specific information naming certain companies, FDs, stocks, and with their analytical data."
)


        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=message_content
        )
    except Exception as e:
        return jsonify({'error': f'Error adding message: {e}'}), 500

    try:
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant_id
        )
    except Exception as e:
        return jsonify({'error': f'Error running thread: {e}'}), 500

    if run.status == "completed":
        try:
            messages_response = client.beta.threads.messages.list(thread_id=thread.id)
            
            response_json = {"messages": []}
            
            if hasattr(messages_response, 'data') and isinstance(messages_response.data, list):
                for message in messages_response.data:
                    if message.role == 'assistant':
                        message_dict = {"id": message.id, "content": ""}
                        if hasattr(message, 'content') and isinstance(message.content, list):
                            content_list = []
                            for content_block in message.content:
                                if hasattr(content_block, 'text') and hasattr(content_block.text, 'value'):
                                    content_list.append(content_block.text.value)
                            message_dict["content"] = " ".join(content_list)
                        response_json["messages"].append(message_dict)
            
            return jsonify(response_json)
        
        except Exception as e:
            return jsonify({'error': f'Error listing messages: {e}'}), 500
    else:
        try:
            return jsonify({'run_details': run.to_json()})
        except Exception as e:
            return jsonify({'error': f'Error fetching run details: {e}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080)