# llm_chain.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from prompts import VACATION_PROMPT

class VacationPlanner:
    def __init__(self, api_key):
        # Gemini 3 Flash for speed and long-context memory
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview", 
            google_api_key=api_key,
            temperature=0.7
        )
        
        # We use ChatPromptTemplate to handle a sequence of messages (History)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", VACATION_PROMPT), # The instructions
            MessagesPlaceholder(variable_name="chat_history"), # Where the past chat lives
            ("human", "{input}") # The user's latest request
        ])
        
        # Modern LCEL Chain
        self.chain = self.prompt | self.llm | StrOutputParser()

    def generate_itinerary(self, destination, budget, days, travel_type, interests, chat_history=[]):
        """
        Generates or refines an itinerary based on chat history.
        """
        # Convert the session_state messages into LangChain message objects
        formatted_history = []
        for msg in chat_history:
            if msg["role"] == "user":
                formatted_history.append(HumanMessage(content=msg["content"]))
            else:
                formatted_history.append(AIMessage(content=msg["content"]))

        # Creating the initial context if it's the first run
        user_input = f"Plan a trip to {destination} for {days} days with a budget of {budget}. Style: {travel_type}. Interests: {interests}"
        
        # If it's a follow-up, the 'interests' parameter from app.py will contain the 'Edit' request
        if "Modify" in interests or "REVISE" in interests:
            user_input = interests

        return self.chain.invoke({
            "chat_history": formatted_history,
            "input": user_input
        })