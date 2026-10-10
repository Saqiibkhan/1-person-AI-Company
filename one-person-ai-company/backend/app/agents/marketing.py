def build_marketing_agent(llm):
    from crewai import Agent

    return Agent(
        role="Marketing / Strategy Agent",
        goal=(
            "Turn research and requirements into a practical, actionable "
            "business or marketing strategy."
        ),
        backstory=(
            "You are an experienced marketing strategist. You build on "
            "approved research rather than repeating it, and you produce "
            "concrete recommendations, not vague generalities."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )
