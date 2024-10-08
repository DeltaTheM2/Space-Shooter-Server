from flask import Flask, jsonify, request
from openai import OpenAI
import os
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()

KEPT_QUERY = ""
LAST_THREAD_ID = None
OpenaiApiKey = os.environ.get('OPENAI_API_KEY')
client = OpenAI()

my_assistant = client.beta.assistants.retrieve("asst_7bHMEyumWTDCjprU3gpBjVqs")

app = Flask(__name__)
CORS(app)
@app.route("/query/<query>", methods=['GET'])
def respondToQuery(query):
    global KEPT_QUERY, LAST_THREAD_ID

    # If the query is new, create a new thread
    if query != KEPT_QUERY:
        KEPT_QUERY = query
        my_thread = client.beta.threads.create()
        LAST_THREAD_ID = my_thread.id
    else:
        # If the query is the same, use the existing thread
        if LAST_THREAD_ID is None:
            return jsonify({"error": "No existing thread to continue."})
        my_thread = client.beta.threads.retrieve(LAST_THREAD_ID)


    my_message = client.beta.threads.messages.create(
          thread_id=my_thread.id,
          role= 'user',
          content= query
        )
    
    my_run = client.beta.threads.runs.create(
  thread_id=my_thread.id,
  assistant_id=my_assistant.id,
)
    print(f"This is the run object: {my_run} \n")

    # Step 5: Periodically retrieve the Run to check on its status to see if it has moved to completed
    while my_run.status in ["queued", "in_progress"]:
        keep_retrieving_run = client.beta.threads.runs.retrieve(
            thread_id=my_thread.id,
            run_id=my_run.id
        )
        print(f"Run status: {keep_retrieving_run.status}")

        if keep_retrieving_run.status == "queued" or keep_retrieving_run.status == "in_progress":
            pass
        else:
            print(f"Run status: {keep_retrieving_run.status}")
            break

    if keep_retrieving_run.status == "completed":
            print("\n")

            # Step 6: Retrieve the Messages added by the Assistant to the Thread
            all_messages = client.beta.threads.messages.list(
                thread_id=my_thread.id
            )

            print("------------------------------------------------------------ \n")

            print(f"User: {my_message.content[0].text.value}")
            print(f"Assistant: {all_messages.data[0].content[0].text.value}")
            response = all_messages.data[0].content[0].text.value
            resp = response.strip()
            return resp
#resetting the global variables to ensure every time the server refreshes.
@app.route("/end", methods=['GET'])
def endQuery():
    KEPT_QUERY = ""
    LAST_THREAD_ID = ""
    return "Thread Reset successfully"

@app.route('/ResetThread', methods=['GET'])
def resetThread():
    global LAST_THREAD_ID
    client.beta.threads.delete(thread_id= str(LAST_THREAD_ID))

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=8080)
