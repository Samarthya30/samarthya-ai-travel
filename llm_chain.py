# llm_chain.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from prompts import VACATION_PROMPT

class VacationPlanner:
    def __init__(self, api_key):
        # Using Gemini 1.5 Flash for speed and high-context reasoning
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            google_api_key=api_key,
            temperature=0.7
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", VACATION_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{user_notes}") 
        ])
        
        self.chain = self.prompt | self.llm | StrOutputParser()

    def generate_itinerary(self, destination, budget, days, travel_type, interests, chat_history):
        # Format the session state messages into LangChain Message objects
        formatted_history = []
        for msg in chat_history:
            if msg["role"] == "user":
                formatted_history.append(HumanMessage(content=msg["content"]))
            else:
                formatted_history.append(AIMessage(content=msg["content"]))

        # Execute Chain
        # Note: 'interests' fills the {interests} slot in the System Prompt
        # 'user_notes' fills the {user_notes} slot in the Human Message
        return self.chain.invoke({
            "destination": destination,
            "budget": budget,
            "days": days,
            "travel_type": travel_type,
            "interests": interests,    
            "user_notes": interests,   
            "chat_history": formatted_history
        })