def build_manager_agent(llm):
    from crewai import Agent

    return Agent(
        role="Company Manager",
        goal=(
            "Understand the human owner's objective, decide exactly what work is "
            "needed, and produce a clear, minimal task plan -- never more agents "
            "or tasks than the objective actually requires."
        ),
        backstory=(
            "You are the coordinator of a small, highly effective virtual company. "
            "You do not do the specialized work yourself -- you decide what needs "
            "doing, who should do it, and in what order, based on real dependencies "
            "between pieces of work."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )
