from google.adk.agents import LlmAgent, LoopAgent


MODEL = "gemini-2.0-flash"


idea_agent = LlmAgent(
    model=MODEL,
    name="idea_agent",
    instruction=f"""Eres un agente de ideas. Haz una lluvia de ideas y sé creativo""",
    disallow_transfer_to_peers=False,
)

refiner_agent = LlmAgent(
    model=MODEL,
    name="refiner_agent",
    instruction="""Eres responsable de refinar las ideas generadas por el agente "idea_agent".""",
    disallow_transfer_to_peers=False,
)

root_agent = LlmAgent(
    model=MODEL,
    name="planner_agent",
    instruction=f"""Eres un estratega de negocios y especialista en crear sistemas
    que automatizan procesos y optimizan resultados.
    Después de recibir la respuesta del agente "idea_agent", SIEMPRE
    utiliza el agente "refiner_agent" para refinar la idea.
    """,
    sub_agents=[idea_agent, refiner_agent],
)
# También puedes usar LoopAgent para crear un agente que itere sobre los sub-agentes.
# root_agent = LoopAgent(
#     name="planner_agent",
#     sub_agents=[idea_agent, refiner_agent],
#     max_iterations=3
# )
