import logging
from agents import Agent, Runner, set_default_openai_key
from tenacity import retry, stop_after_attempt, wait_exponential
from core.config import settings
from prompts.planner_eval_prompt import build_planner_eval_prompt
from models.schemas import PlanEvaluation, TripPlan, TripRequest, EvaluationIssue

logger = logging.getLogger(__name__)

set_default_openai_key(settings.openai_api_key)

# AI-powered evaluator to evaluate the trip itinerary.
# Some issues are warnings, some are blockers.
class PlannerEvaluator:
    _agent = Agent(
        name="TripPlannerEvaluator",
        instructions="""
You are a travel itinerary quality evaluator.

You will be given a trip request and a generated itinerary. Your job is to critically evaluate the itinerary and return structured feedback.
Check for the following issues:
- Budget (blocking): If a budget is provided, the trip total must not exceed it. Flag if it does.
- Day count (blocking): The number of days in the itinerary must match the number of days in the trip (start_date to end_date inclusive). Flag if they don't match.
- Exclusions (blocking): If the request has an exclude list, no activity, restaurant, or location in the itinerary should match anything on that list.
- Meals (blocking): Every full day must include breakfast, lunch, and dinner. Flag any day that is missing a meal.
- Pacing (warning): Flag any day that has an unrealistic number of activities (more than ~6-7 items in a single day is likely overloaded).
- Specificity (warning): Flag activities that are too generic (e.g. "visit a museum", "eat at a restaurant"). Activities should reference real, named places.
- Variety (warning): Flag if the itinerary is repetitive — for example, multiple consecutive days with the same type of activity, or the same cuisine appearing at more than two meals. Variety does not apply to lodging — staying at the same hotel throughout the trip is expected and correct.

Set `passed` to true only if there are zero blocking issues. Warnings alone should not cause a failure.
""",
        model="gpt-4o",
        output_type=PlanEvaluation
    )

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _run_agent(prompt) -> PlanEvaluation:
        return await Runner.run(PlannerEvaluator._agent, prompt)

    @staticmethod
    async def evaluate(
        trip_plan: TripPlan,
        trip_request: TripRequest
    ) -> tuple[bool, list[EvaluationIssue]]:
        # Generate the specific prompt for our evaluator agent.
        # This prompt will have the trip plan and request interpolated
        # in so the AI can properly evaluate it.
        prompt = build_planner_eval_prompt(trip_plan, trip_request)

        # Run our agent, and pull out the results as evaluation
        result = await PlannerEvaluator._run_agent(prompt)
        evaluation: PlanEvaluation = result.final_output
        # Return a tuple of evaluation status (bool) and list of issues
        return (evaluation.passed, evaluation.issues)

