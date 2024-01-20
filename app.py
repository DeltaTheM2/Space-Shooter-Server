from flask import Flask, jsonify, request
import openai
import os

OpenaiApiKey = os.environ.get('OpenaiApiKey')
client = openai.Client(api_key=OpenaiApiKey)

my_assistant = client.beta.assistants.retrieve("asst_7bHMEyumWTDCjprU3gpBjVqs")

app = Flask(__name__)
@app.route("/query/<query>")
def respondToQuery(query):
    my_thread = client.beta.threads.create()

    my_message = client.beta.threads.messages.create(
          thread_id=my_thread.id,
          role= 'user',
          content= query
        )
    
    my_run = client.beta.threads.runs.create(
  thread_id=my_thread.id,
  assistant_id=my_assistant.id,
  instructions= my_thread.instructions
)
    print(f"This is the run object: {my_run} \n")

    # Step 5: Periodically retrieve the Run to check on its status to see if it has moved to completed
    while my_run.status in ["queued", "in_progress"]:
        keep_retrieving_run = client.beta.threads.runs.retrieve(
            thread_id=my_thread.id,
            run_id=my_run.id
        )
        print(f"Run status: {keep_retrieving_run.status}")

        if keep_retrieving_run.status == "completed":
            print("\n")

            # Step 6: Retrieve the Messages added by the Assistant to the Thread
            all_messages = client.beta.threads.messages.list(
                thread_id=my_thread.id
            )

            print("------------------------------------------------------------ \n")

            print(f"User: {my_message.content[0].text.value}")
            print(f"Assistant: {all_messages.data[0].content[0].text.value}")

            break
        elif keep_retrieving_run.status == "queued" or keep_retrieving_run.status == "in_progress":
            pass
        else:
            print(f"Run status: {keep_retrieving_run.status}")
            break

if __name__ == '__main__':
   app.run(host='0.0.0.0')


