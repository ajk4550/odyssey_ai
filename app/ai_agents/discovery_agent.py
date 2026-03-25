import logging
from agents import Agent, Runner, set_default_openai_key
from tenacity import retry, stop_after_attempt, wait_exponential
from core.config import settings
from prompts.discovery_prompt import build_discovery_prompt
from models.schemas import TripDiscoveryRequest, TripDiscoveryResponse
from tools.travel_time_tool import get_travel_time
from ai_agents.discovery_evaluator import evaluate

logger = logging.getLogger(__name__)

set_default_openai_key(settings.openai_api_key)

class DiscoveryAgent:
    _agent = Agent(
        name="TripDiscoveryAgent",
        instructions="""
You are a travel destination expert.

Your job is to suggest exactly 5 travel destinations based on the user's criteria. You must always return exactly 5, no more and no less.

Follow these principles:
- Suggest destinations that match the vacation type and interests.
- Consider the user's budget - factor in travel costs from their origin.
- Consider the month - recommend destinations with good weather that time of year.
- Use the get_travel_time tool to provide accurate travel times from the user's origin.
- When using get_travel_time, always pass a city or town name (e.g. "Laconia, NH" not "Lake Winnipesaukee, NH").
- Keep reasons concise but specific to why it matches their criteria.
- Never suggest destinations in the excluded locations. Treat exclusions as full names, abbreviations, and partial matches — for example, if "New York" is excluded, do not suggest any destination in New York state, including those labeled with ", NY".
- If a max travel time is specified, you MUST use get_travel_time to verify travel time before including any destination. Never suggest a destination that exceeds the limit.
- Always populate travel_time_minutes with the exact minutes value returned by get_travel_time.
""",
        model="gpt-4o",
        output_type=TripDiscoveryResponse,
        tools=[get_travel_time]
    )

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _run_agent(prompt):
        return await Runner.run(DiscoveryAgent._agent, prompt)

    @staticmethod
    async def generate_suggestions(request: TripDiscoveryRequest) -> TripDiscoveryResponse:
        prompt = build_discovery_prompt(request)

        # Keeping track of the best attempt and using feedback lines to gauge that.
        best = None
        best_issue_count = float("inf")

        for attempt in range(3):
            result = await DiscoveryAgent._run_agent(prompt)
            response = result.final_output
            passed, issues = evaluate(response, request)

            if passed:
                return response

            if len(issues) < best_issue_count:
                best = response
                best_issue_count = len(issues)

            feedback = "Your previous response had the following issues:\n"
            feedback += "\n".join(f"- {issue}" for issue in issues)
            feedback += "\nPlease try again and fix all of these issues."

            logger.warning(f"Discovery attempt {attempt + 1} failed evaluation: {feedback}")
            prompt = prompt + f"\n\n{feedback}"

        logger.warning("All attempts failed evaluation, returning the best result")
        return best
