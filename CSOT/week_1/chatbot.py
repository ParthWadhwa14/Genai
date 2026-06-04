import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

def run_chatbot():
    """
    A terminal chatbot that holds a coherent multi-turn conversation.

    Your implementation should:
    - Start with a system message that sets the assistant's behaviour.
    - Maintain a `messages` list with alternating user/assistant turns.
    - Append the assistant's reply to `messages` after each call.
    - Resend the full history on every API call.
    - Allow the user to type 'exit' or 'quit' to end the session.

    Stretch:
    - Add a '/reset' command that clears history so you can feel context loss live.
    - Add a '/tokens' command that prints response.usage after the last call.
    """
    
    def conversation_correction(conversation_history):
        new_history=[]
        summerizer=client.chat.completions.create(
            model="nvidia/nemotron-3-super-120b-a12b:free",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a helpful ai assistant. Your task is to summarize the following conversation between a user and an assistant. The summary should be concise but retain all important facts, names, and context."
                },
                {
                    "role": "user", 
                    "content": f"""Here is the conversation history:
                    {conversation_history}
                    Please provide a concise summary of this conversation."""}
            ]
        )
        summary=summerizer.choices[0].message.content
        
        new_history = [
            {"role": "system", "content": "You are a helpful ai assistant"},
            {"role": "user", "content": f"Here is a summary of our earlier chat: {summary}"},
        ]
        new_history.append(conversation_history[-1])
        return new_history
    
    conversation_history = [{"role": "system", "content": "You are a helpful ai assistant, do not answer anything useless or unasked for."}]
    while True:
        prompt = input("[YOU] ")
        
        if prompt.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break
        if prompt.lower() == '/reset':
            conversation_history = [{"role": "system", "content": "You are a helpful ai assistant"}]
            print("\n[SYSTEM: History wiped. Clean slate.]\n")
            continue
        if prompt.lower() == '/tokens':
            if response and hasattr(response, 'usage'):
                print(response.usage)
            else:
                print("[SYSTEM: Token usage is not available.]")
            continue
        conversation_history.append({"role": "user", "content": prompt})
        
        if len(conversation_history) > 10:
            conversation_history = conversation_correction(conversation_history)
    
        response = client.chat.completions.create(
            model="nvidia/nemotron-3-super-120b-a12b:free",
            messages=conversation_history,
            stream=True
        )
        
        print("[MODEL] ", end="")
        full_response = "" 
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                chunk_text = chunk.choices[0].delta.content
                print(chunk_text, end="", flush=True)
                full_response += chunk_text
                
        print("\n") 
        conversation_history.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    print("Chat started. Type 'exit' to quit.\n")
    run_chatbot()
    
    
    
    
    
