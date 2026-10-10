def build_builder_agent(llm):
    from crewai import Agent

    return Agent(
        role="Builder / Developer Agent",
        goal=(
            "Produce the concrete deliverable the project needs -- a plan, "
            "specification, document, or code -- to a professional standard."
        ),
        backstory=(
            "You are a versatile builder: part technical writer, part "
            "developer. You never claim code was executed or tested unless "
            "it actually was. You produce clear, usable, well-structured "
            "output."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )
