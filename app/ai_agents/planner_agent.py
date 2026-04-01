import logging
from core.config import settings 
from agents import Agent, Runner, set_default_openai_key
from prompts.planner_prompt import build_planner_prompt
from models.schemas import TripPlan, TripRequest
from tenacity import retry, stop_after_attempt, wait_exponential
from tools.travel_time_tool import get_travel_time
from tools.events_tool import get_destination_activities
from ai_agents.planner_evaluator import PlannerEvaluator

logger = logging.getLogger(__name__)

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
- Use get_destination_activities to look up real attractions and events at the destination.
- Incorporate specific events happening during the trip dates into the itinerary where relevant.
- Do not limit suggestions to the user's stated interests — a user interested in hiking
  might still enjoy a local festival or sports event. Use judgment.
- Prefer named, specific activities over generic ones (e.g. "Visit the Isabella Stewart
  Gardner Museum" over "Visit a museum").
- Do not schedule more than one ticketed evening event per day.
- Include breakfast, lunch, and dinner for each full day of the trip.
- Suggest high-value experiences appropriate to the destination and budget — for example, a Broadway show in NYC or a wine tour in Napa.
- On the final day of the trip, do not book lodging. The last day should include checkout and return travel home.
""",
            model="gpt-4o",
            output_type=TripPlan,
            tools=[get_travel_time, get_destination_activities]
        )

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _run_agent(prompt):
        return await Runner.run(PlannerAgent._agent, prompt)

    @staticmethod
    async def generate_plan(trip_request: TripRequest) -> TripPlan:
        # Generate the prompt that the LLM will receive
        prompt = build_planner_prompt(trip_request)

        # Keeping track of the best attempt and using feedback lines to gauge that.
        best = None
        best_issue_count = float("inf")

        # Trying up to 3 times to generate an itinerary
        # This utilizes an AI Powered Evaluator
        for attempt in range(3):
            # Call the planner agent with the generated prompt. Output
            # should be a TripPlan
            result = await PlannerAgent._run_agent(prompt)
            trip_plan: TripPlan = result.final_output
            # Pass the trip plan and the original request to the evaluator
            passed, issues = await PlannerEvaluator.evaluate(trip_plan, trip_request)

            # If we passed, stopped trying and return the trip_plan just generated
            if passed:
                return trip_plan

            # Compare our best response to the current.
            if len(issues) < best_issue_count:
                best = trip_plan
                best_issue_count = len(issues)

            # Generate feedback for LLM based on issues found.
            feedback = "Your previous response had the following issues:\n"
            feedback += "\n".join(f"- [{issue.severity}] {issue.description}" for issue in issues)
            feedback += "\nPlease try again and fix all of these issues."

            logger.warning(f"Planner attempt {attempt + 1} failed evaluation: {feedback}")
            prompt = prompt + f"\n\n{feedback}" # Add our feedback to the prompt for LLM

        # If we reached here, we tried 3 times and didn't get a passable result
        # Return our best result instead
        logger.warning("All attempts failed evaluation, returning the best result")
        return best
