import autogen
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import (
    RetrieveUserProxyAgent,
)
from flask import Flask, jsonify, request
from flask_cors import cross_origin
import multiprocessing as mp
from openai import AuthenticationError
from spaCySimilarity import store_docs, compare_new_doc

###### Set up Routes

CUSTOM_PROMPT = """
You're a retrieve augmented assistant for answering frequently asked questions. You answer user's questions based on your own knowledge and the
Frequently Asked Questions provided by the user.

If you cannot provide an answer using the context given by the user you must reply with
'Sorry, there is no information on <what the user asked> in the frequently asked questions.'

You must follow these rules with your output:
* You must put \n\r between numbered lists of bullet points
* You must structure your response into paragraphs, separated by \n\r

Your answer should be as concise as possible. Your answer must not exceed 100 words.

User's question is: {input_question}

Frequently Asked Questions: {input_context}
"""

SIMILARITY_THRESHOLD = 0.86
CACHE_FILE_NAME = "faqs"
EXTRA_STOPS = ["certificate", "lost"]

app = Flask(__name__)

@app.route('/questions', methods=['POST'])
@cross_origin()
def ask_question():
    item = request.get_json()
    if not item['question']:
        return jsonify({
            'error': 'Invalid request'
        }), 500

    question = item['question']
    cacheHit = cache_check(question, SIMILARITY_THRESHOLD)

    if (cacheHit):
        return jsonify({
            'cacheHit': True,
            'answeredQuestion': cacheHit['question'],
            'actualQuestion': question,
            'answer': cacheHit['answer']
        })

    answer = agent_reply(question)[0]
    cache_response(question, answer)

    return jsonify({
        'cacheHit': False,
        'answer': answer
    })

def cache_check(question, threshold):
    cacheResult = compare_new_doc(question, CACHE_FILE_NAME, EXTRA_STOPS)

    if not cacheResult:
        return None

    if (cacheResult['similarity'] > threshold):
        print("INFO: Cache hit for '" + question + "' with similarity" + str(cacheResult['similarity']))
        return {
            'question': cacheResult['question'],
            'answer' : cacheResult['answer']
        }
    
    return None

def cache_response(question, answer):
    print("INFO: Caching response for '" + str(question) +"'")
    store_docs([question], [answer], CACHE_FILE_NAME, EXTRA_STOPS)

###### Configure Autogen

global ragproxyagent, assistant

DOCS_PATH="./docs/"
TIMEOUT=60
# gpt-3.5-turbo
MODEL = "gpt-4"

def initialize_agents(llm_config, docs_path): 
   
    assistant = RetrieveAssistantAgent(
        name="assistant",
        system_message="You are a helpful assistant.",
        llm_config=llm_config
    )

    ragproxyagent = RetrieveUserProxyAgent(
        name="ragproxyagent",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=5,
        retrieve_config={
            "model": "gpt-3.5-turbo",
            "code_execution_context": False,
            "task": "qa",
            "customized_prompt": CUSTOM_PROMPT,
            "docs_path": docs_path,
        },
    )

    return ragproxyagent, assistant

def initiate_chat(questionString, queue):
    assistant.reset()
    try:
        ragproxyagent.initiate_chat(assistant, problem=questionString, n_results=3)

        messages = ragproxyagent.chat_messages
        messages = [messages[k] for k in messages.keys()][0]
        messages = [m["content"] for m in messages if m["role"] == "user"]
        print("messages: ", messages)
        queue.put(messages)

    except AuthenticationError as e:
        print('FATAL: OPEN AI AUTHENTICATION ERROR ' + e.message)

    except Exception as e:
        print("ERROR: " + str(e))

def agent_reply(question): 
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
        print("ERROR: " + error)

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
    model_api_key_map = {
        "gpt-4": "MY_OAI_KEY",
        "gpt-3.5-turbo": "MY_OAI_KEY"
    }
)

if not any(config.get('api_key') for config in config_list):
    raise ValueError("No API keys found. Please check your openai.env file. " +
                     "If you don't have one you need to create one by copying openai.example.env" +
                     "and entering an Open AI API key.")

print(config_list)

llm_config = {
    "timeout": TIMEOUT,
    "cache_seed": 42,
    "config_list": config_list,
    "temperature": 0,
    "max_retries" : 2,
}

ragproxyagent, assistant = initialize_agents(llm_config, DOCS_PATH)

###### Run web application
if __name__ == '__main__':
    app.run(debug=True)
