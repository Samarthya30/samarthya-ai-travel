# llm_chain.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from prompts import VACATION_PROMPT

class VacationPlanner:
    def __init__(self, api_key):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview", 
            google_api_key=api_key,
            temperature=0.7
        )
        
        # We ensure the template knows exactly what variables to expect
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", VACATION_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        self.chain = self.prompt | self.llm | StrOutputParser()

    def generate_itinerary(self, destination, budget, days, travel_type, interests, chat_history):
        # Convert history
        formatted_history = []
        for msg in chat_history:
            role = HumanMessage if msg["role"] == "user" else AIMessage
            formatted_history.append(role(content=msg["content"]))

        # We pass EVERYTHING the prompt needs in one dictionary
        return self.chain.invoke({
            "destination": destination,
            "budget": budget,
            "days": days,
            "travel_type": travel_type,
            "input": interests, # This maps to the {input} in ChatPromptTemplate
            "chat_history": formatted_history
        })