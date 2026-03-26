from core.config import settings 
from agents import Agent, Runner, set_default_openai_key
from prompts.planner_prompt import build_planner_prompt
from models.schemas import TripPlan
from tenacity import retry, stop_after_attempt, wait_exponential
from tools.travel_time_tool import get_travel_time

set_default_openai_key(settings.openai_api_key)

class PlannerAgent:
    _agent = Agent(
            name="TripPlannerAgent",
            instructions="""
You are an expert travel planner.

Your job is to generate thoughtful travel itineraries based on user trip requests.

Follow these principles:
- Create realistic daily plans.
- Ensure the itinerary fits within the travel dates.
- Keep recommendations consistent with the user's budget.
- Balance sightseeing, food, and relaxation.
- Always produce output that matches the required schema.
- Ensure the number of days in the itinerary matches the trip duration.
- Avoid overloading a single day with too many activities.
- Include a variety of activities, paying attention to the users interests in particular.
- If the exclusion list includes activities, don't include those in the itinerary.
- Use the get_travel_time tool to calculate realistic travel times between locations when planning multi-destination itineraries.
""",
            model="gpt-4o",
            output_type=TripPlan,
            tools=[get_travel_time]
        )

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _run_agent(prompt):
        return await Runner.run(PlannerAgent._agent, prompt)

    @staticmethod
    async def generate_plan(trip_request):
        # Generate the prompt that the LLM will receive
        prompt = build_planner_prompt(trip_request)

        # Call the planner agent with the generated prompt. Output
        # should be a TripPlan
        result = await PlannerAgent._run_agent(prompt)
        trip: TripPlan = result.final_output

        return trip
