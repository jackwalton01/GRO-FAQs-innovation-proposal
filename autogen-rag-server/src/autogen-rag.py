import autogen
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from flask import Flask, jsonify, request

global ragproxyagent
global assistant

# You can use send or initiate_chat(clear_history=False) to continue the conversation
def question(questionString):
  assistant.reset()
  ragproxyagent.initiate_chat(assistant, problem=questionString)

app = Flask(__name__)

# A simple in-memory data store
data = {
    'items': []
}

@app.route('/questions', methods=['POST'])
def ask_question():
    item = request.get_json()
    print('Request Received: ' + item['question'])
    
    return jsonify(item), 201

# Retrieve an 
config_list = autogen.config_list_from_dotenv(
  dotenv_file_path = "./openai.env",
    filter_dict={
        "model": {
            "gpt-3.5-turbo"
        }
    },
    model_api_key_map = {
        # "gpt-4": "OPENAI_API_KEY",
        "gpt-3.5-turbo": "MY_OAI_KEY"
    }
)

llm_config = {
    "timeout": 60,
    "cache_seed": 42,
    "config_list": config_list,
    "temperature": 0,
    "max_retries" : 2,
}

print(config_list)

# can altering the system message be used to tailor the behavior of the AI?
# to best answer user questions.

# does not directly interact with the model, instead uses documents retrieved by the user proxy agent
assistant = RetrieveAssistantAgent(
    name="assistant",
    system_message="You are a helpful assistant.",
    llm_config=llm_config
)

# TODO can't push up an open AI key, so should have an error response saying no open AI key was found!

# TODO look into this, we should have this set somewhere so that we can't execute code!
# code_execution_context=False



ragproxyagent = RetrieveUserProxyAgent(
    name="ragproxyagent",
    retrieve_config={
        "model": "gpt-3.5-turbo",
        "task": "qa",
        "docs_path": "../docs/gro-faqs.html",
    },
)


if __name__ == '__main__':
    app.run(debug=True)