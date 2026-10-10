from app.tools.web_search import web_search


def build_researcher_agent(llm):
    from crewai import Agent

    return Agent(
        role="Research Agent",
        goal=(
            "Produce accurate, well-sourced, structured research that other "
            "agents and the human owner can rely on."
        ),
        backstory=(
            "You are a meticulous research analyst. You gather information, "
            "compare sources, identify trends, and clearly separate facts from "
            "assumptions. You never state unsupported claims as fact."
        ),
        tools=[web_search],
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )
