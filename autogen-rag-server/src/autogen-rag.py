import autogen
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import (
    RetrieveUserProxyAgent,
)
from flask import Flask, jsonify, request
from flask_cors import cross_origin
import multiprocessing as mp

###### Set up Routes

# If your answer consists of 2 or more paragraphs then at the beginning of your answer you must include a summary of your answer in the following format
# <b>Summary</b><br>Your summary<br><b>Further Information</b><br>The rest of your answer...

CUSTOM_PROMPT = """
You're a retrieve augmented assistant for answering frequently asked questions. You answer user's questions based on your own knowledge and the
context provided by the user.
If you can't answer the question with or without the current context, you should reply exactly `UPDATE CONTEXT`.

You must follow these rules with your output:
* You must put \n\r between numbered lists of bullet points
* You must structure your response into paragraphs, separated by \n\r

Your answer should be as concise as possible. Your answer must not exceed 100 words.

User's question is: {input_question}

Context is: {input_context}
"""
app = Flask(__name__)

@app.route('/questions', methods=['POST'])
@cross_origin()
def ask_question():
    item = request.get_json()

    if item['question']:
        return jsonify({
            'answer': chatbot_reply(item['question'])
        })
    else:
        return jsonify({
            'error': 'Request did not have a property: \'question\''
        }), 500

###### Configure Autogen

global ragproxyagent, assistant

DOCS_PATH="./docs/"
TIMEOUT=60
MODEL = "gpt-3.5-turbo" # 3.5-turbo

def initialize_agents(llm_config, docs_path): 
   
    assistant = RetrieveAssistantAgent(
        name="assistant",
        system_message="You are a helpful assistant.",
        llm_config=llm_config
    )

    # We might need to set max_consecutive_auto_reply=1 to get one reply
    ragproxyagent = RetrieveUserProxyAgent(
        name="ragproxyagent",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=5,
        retrieve_config={
            "model": "gpt-3.5-turbo",
            "task": "qa",
            "customized_prompt": CUSTOM_PROMPT,
            "docs_path": docs_path,
        },
    )

    return ragproxyagent, assistant

# TODO Consider asking the AI to format it's response so it is more Humanly Readable

# TODO Maintain a conversation history to improve performance.
# This will mean that we can give the AI the context when we load up the service
# And then just append user questions when they send a new question!
def initiate_chat(questionString, queue):

    # TODO check we have a valid API key

    assistant.reset()
    try:
        # TODO n_results parameter can be used to control how many chunks of the document that relate to the query
        # are retrieved and used to consider the answer.
        ragproxyagent.initiate_chat(assistant, problem=questionString, n_results=3)

        messages = ragproxyagent.chat_messages
        messages = [messages[k] for k in messages.keys()][0]
        messages = [m["content"] for m in messages if m["role"] == "user"]
        print("messages: ", messages)

    except(e):
        print(str(e))

    queue.put(messages)

def chatbot_reply(question): 
    queue = mp.Queue()
    process = mp.Process(
        target=initiate_chat,
        args=(question, queue),
    )
    process.start()

    try:
        messages = queue.get(timeout=TIMEOUT)
    except Exception as e:
        error = [str(e) if len(str(e)) > 0 else "Invalid Request to OpenAI, please check your API keys."]
        print(error)

    finally:
        try:
            process.terminate()
        except:
            pass
    
    return messages

# Retrieve the open ai key from the env file and build a config
config_list = autogen.config_list_from_dotenv(
    dotenv_file_path = "./openai.env",
    filter_dict={
        "model": {
            MODEL
        }
    },
     # TODO lets have a proper parameter that decides that model to use...
    model_api_key_map = {
        "gpt-4": "MY_OAI_KEY",
        "gpt-3.5-turbo": "MY_OAI_KEY"
    }
)

print(config_list)

llm_config = {
    "timeout": TIMEOUT,
    "cache_seed": 42,
    "config_list": config_list,
    "temperature": 0,
    "max_retries" : 2,
}

ragproxyagent, assistant = initialize_agents(llm_config, DOCS_PATH)

# initiate_chat('Hey AI, How can i get a marriage certificate?')

# TODO can't push up an open AI key, so should have an error response saying no open AI key was found!

# TODO look into this, we should have this set somewhere so that we can't execute code!
# code_execution_context=False

# (TODO talk about this in readme) We can also add a custom prompt to the API to explain how it should answer questions
# Currently we are using Microsoft's default prompt for a RAG agent.

###### Run web application

if __name__ == '__main__':
    app.run(debug=True)
