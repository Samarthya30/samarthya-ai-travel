# llm_chain.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from prompts import VACATION_PROMPT

class VacationPlanner:
    def __init__(self, api_key):
        # Using Gemini 3 Flash (the latest 2026 stable version)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview", 
            google_api_key=api_key,
            temperature=0.7
        )
        
        # Updated input_variables to include 'dietary' and 'pace'
        self.prompt = PromptTemplate(
            input_variables=["destination", "budget", "days", "travel_type", "interests"],
            template=VACATION_PROMPT
        )
        
        # Modern LCEL Chain
        self.chain = self.prompt | self.llm | StrOutputParser()

    def generate_itinerary(self, destination, budget, days, travel_type, interests):
        # 'interests' here will now be the 'refined_interests' string from app.py
        # which already contains the food and pace details.
        return self.chain.invoke({
            "destination": destination,
            "budget": budget,
            "days": days,
            "travel_type": travel_type,
            "interests": interests
        })