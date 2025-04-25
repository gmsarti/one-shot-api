import random
from enum import Enum
from typing import Optional, TypedDict

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph

from one_shot_api.config.llm import default_llm_config


class SettingType(str, Enum):
    LOW_FANTASY = "low_fantasy"
    HIGH_FANTASY = "high_fantasy"
    MODERN_WAR = "modern_war"
    SUPER_HEROES = "super_heroes"
    URBAN_FANTASY = "urban_fantasy"
    SCI_FI = "sci_fi"
    HORROR = "horror"
    WESTERN = "western"


class ToneType(str, Enum):
    SERIOUS = "serious"
    HUMOROUS = "humorous"
    DARK = "dark"
    LIGHTHEARTED = "lighthearted"
    GRITTY = "gritty"
    EPIC = "epic"


class PowerLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class StoryState(TypedDict):
    """State for the story generation system."""

    player_count: int
    power_level: PowerLevel
    setting: SettingType
    tone: ToneType
    region: str
    main_location: str
    adversary: str
    adversary_minions: str
    third_party: str
    reward: str
    plot: str


def determine_player_count(
    state: StoryState, player_count: Optional[int] = None
) -> StoryState:
    """Determine the number of players for the one-shot."""
    if player_count is not None:
        return {**state, "player_count": player_count}

    return {**state, "player_count": random.randint(3, 6)}


def determine_power_level(
    state: StoryState, power_level: Optional[PowerLevel] = None
) -> StoryState:
    """Determine the power level of the characters."""
    if power_level is not None:
        return {**state, "power_level": power_level}

    return {**state, "power_level": random.choice(list(PowerLevel)).value}


def determine_setting(
    state: StoryState, setting: Optional[SettingType] = None
) -> StoryState:
    """Determine the setting for the story."""
    if setting is not None:
        return {**state, "setting": setting}

    return {**state, "setting": random.choice(list(SettingType)).value}


def determine_tone(state: StoryState, tone: Optional[ToneType] = None) -> StoryState:
    """Determine the tone of the story."""
    if tone is not None:
        return {**state, "tone": tone}

    return {**state, "tone": random.choice(list(ToneType)).value}


def determine_region(state: StoryState) -> StoryState:
    """Determine the overall region where the story takes place."""
    llm = default_llm_config.get_llm()

    prompt = f"""Based on the following criteria:
    - Setting: {state["setting"]}
    - Tone: {state["tone"]}
    - Power Level: {state["power_level"]}

    Generate a brief description of the overall region where the story takes place.
    Return only the region description, nothing else."""

    response = llm.invoke([HumanMessage(content=prompt)])
    return {**state, "region": response.content.strip()}


def determine_main_location(state: StoryState) -> StoryState:
    """Determine the main location where most of the action happens."""
    llm = default_llm_config.get_llm()

    prompt = f"""Based on the following criteria:
    - Setting: {state["setting"]}
    - Tone: {state["tone"]}
    - Region: {state["region"]}

    Generate a brief description of the main location where most of the action will take place.
    Return only the location description, nothing else."""

    response = llm.invoke([HumanMessage(content=prompt)])
    return {**state, "main_location": response.content.strip()}


def determine_adversary(state: StoryState) -> StoryState:
    """Determine the main adversary or villain."""
    llm = default_llm_config.get_llm()

    prompt = f"""Based on the following criteria:
    - Setting: {state["setting"]}
    - Tone: {state["tone"]}
    - Power Level: {state["power_level"]}
    - Main Location: {state["main_location"]}

    Generate a brief description of the main adversary or villain.
    In the description add something that the adversary or villain wants (a thing or a situation) and something that it needs to do to get it.
    Return only the adversary description, nothing else."""

    response = llm.invoke([HumanMessage(content=prompt)])
    return {**state, "adversary": response.content.strip()}


def determine_adversary_minions(
    state: StoryState, minions: Optional[str] = None
) -> StoryState:
    """Determine the adversary's minions or followers."""
    if minions is not None:
        return {**state, "adversary_minions": minions}

    llm = default_llm_config.get_llm()

    prompt = f"""Based on the following criteria:
    - Setting: {state["setting"]}
    - Tone: {state["tone"]}
    - Power Level: {state["power_level"]}
    - Adversary: {state["adversary"]}

    Generate a brief description of the adversary's minions or followers.
    Include their nature, numbers, how and why they serve the adversary.
    Return only the minions description, nothing else."""

    response = llm.invoke([HumanMessage(content=prompt)])
    return {**state, "adversary_minions": response.content.strip()}


def determine_third_party(
    state: StoryState, third_party: Optional[str] = None
) -> StoryState:
    """Determine a third party with their own interests."""
    if third_party is not None:
        return {**state, "third_party": third_party}

    llm = default_llm_config.get_llm()

    prompt = f"""Based on the following criteria:
    - Setting: {state["setting"]}
    - Tone: {state["tone"]}
    - Power Level: {state["power_level"]}
    - Main Location: {state["main_location"]}
    - Adversary: {state["adversary"]}

    Generate a brief description of a third party with their own interests.
    This group should not be aligned with the adversary but may or may not help the players.
    Include their goals and how they might interact with the players.
    Return only the third party description, nothing else."""

    response = llm.invoke([HumanMessage(content=prompt)])
    return {**state, "third_party": response.content.strip()}


def determine_reward(state: StoryState) -> StoryState:
    """Determine the reward for completing the story."""
    llm = default_llm_config.get_llm()

    prompt = f"""Based on the following criteria:
    - Setting: {state["setting"]}
    - Power Level: {state["power_level"]}
    - Adversary: {state["adversary"]}

    Generate a brief description of the reward for completing the story.
    Return only the reward description, nothing else."""

    response = llm.invoke([HumanMessage(content=prompt)])
    return {**state, "reward": response.content.strip()}


def generate_plot(state: StoryState) -> StoryState:
    """Generate the main plot based on all previous decisions."""
    llm = default_llm_config.get_llm()

    prompt = f"""Based on the following criteria, generate a creative and engaging plot for a one-shot RPG story:
    - Number of Players: {state["player_count"]}
    - Power Level: {state["power_level"]}
    - Setting: {state["setting"]}
    - Tone: {state["tone"]}
    - Region: {state["region"]}
    - Main Location: {state["main_location"]}
    - Adversary: {state["adversary"]}
    - Reward: {state["reward"]}

    The plot should be concise but complete, including a clear goal, conflict, and potential resolution.
    Return only the plot description, nothing else."""

    response = llm.invoke([HumanMessage(content=prompt)])
    return {**state, "plot": response.content.strip()}


# Create the workflow
workflow = StateGraph(StoryState)

# Add all the nodes
workflow.add_node("determine_player_count", determine_player_count)
workflow.add_node("determine_power_level", determine_power_level)
workflow.add_node("determine_setting", determine_setting)
workflow.add_node("determine_tone", determine_tone)
workflow.add_node("determine_region", determine_region)
workflow.add_node("determine_main_location", determine_main_location)
workflow.add_node("determine_adversary", determine_adversary)
workflow.add_node("determine_adversary_minions", determine_adversary_minions)
workflow.add_node("determine_third_party", determine_third_party)
workflow.add_node("determine_reward", determine_reward)
workflow.add_node("generate_plot", generate_plot)

# Define the edges
workflow.add_edge("determine_player_count", "determine_power_level")
workflow.add_edge("determine_power_level", "determine_setting")
workflow.add_edge("determine_setting", "determine_tone")
workflow.add_edge("determine_tone", "determine_region")
workflow.add_edge("determine_region", "determine_main_location")
workflow.add_edge("determine_main_location", "determine_adversary")
workflow.add_edge("determine_adversary", "determine_adversary_minions")
workflow.add_edge("determine_adversary_minions", "determine_third_party")
workflow.add_edge("determine_third_party", "determine_reward")
workflow.add_edge("determine_reward", "generate_plot")

# Set the entry point
workflow.set_entry_point("determine_player_count")

# Set the finish point
workflow.set_finish_point("generate_plot")

# Compile the graph
app = workflow.compile()


def generate_story() -> dict:
    """Generate a complete one-shot RPG story."""
    # Run the graph
    result = app.invoke(
        {
            "player_count": 0,
            "power_level": PowerLevel.LOW,
            "setting": SettingType.LOW_FANTASY,
            "tone": ToneType.SERIOUS,
            "region": "",
            "main_location": "",
            "adversary": "",
            "adversary_minions": "",
            "third_party": "",
            "reward": "",
            "plot": "",
        }
    )
    return dict(result)


if __name__ == "__main__":
    # Test the story generator
    print("Generating a one-shot RPG story...")
    result = generate_story()

    print("\nGenerated Story Details:")
    print("-" * 50)
    print(f"Number of Players: {result['player_count']}")
    print(f"Power Level: {result['power_level']}")
    print(f"Setting: {result['setting']}")
    print(f"Tone: {result['tone']}")
    print(f"\n\nRegion: {result['region']}")
    print(f"\nMain Location: {result['main_location']}")
    print(f"\n\nAdversary: {result['adversary']}")
    print(f"\nAdversary's Minions: {result['adversary_minions']}")
    print(f"\n\nThird Party: {result['third_party']}")
    print(f"\n\nReward: {result['reward']}")
    print("\nPlot:")
    print("-" * 50)
    print(result["plot"])
    print("-" * 50)
