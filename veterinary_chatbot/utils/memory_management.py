from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory()

def handle_conversation(query):
    # Retrieve conversation history
    previous_responses = memory.load_memory_variables()
    response = generate_response(query, previous_responses)
    memory.add_user_message(query)
    memory.add_bot_message(response)
    return response
