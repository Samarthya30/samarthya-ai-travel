# llm_chain.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from prompts import VACATION_PROMPT

class VacationPlanner:
    def __init__(self, api_key):
        # Initialize Gemini 2.5 Flash
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            google_api_key=api_key,
            temperature=0.7
        )
        
        self.prompt = PromptTemplate(
            input_variables=["destination", "budget", "days", "travel_type", "interests"],
            template=VACATION_PROMPT
        )
        
        # This is the modern way to "chain" things in 2026 (LCEL)
        # It means: Prompt -> LLM -> Convert output to string
        self.chain = self.prompt | self.llm | StrOutputParser()

    def generate_itinerary(self, destination, budget, days, travel_type, interests):
        # We use .invoke instead of .run in modern LangChain
        return self.chain.invoke({
            "destination": destination,
            "budget": budget,
            "days": days,
            "travel_type": travel_type,
            "interests": interests
        })