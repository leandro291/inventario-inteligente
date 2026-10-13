from fastapi import APIRouter, HTTPException, status

from app.ai.agent import agent
from app.schema.ai import AskIn, AskOut

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/preguntar", response_model=AskOut)
def preguntar(data: AskIn):
    try:
        r = agent.invoke(
            {"messages": [{"role": "user", "content": data.pregunta}]},
            config={"configurable": {"thread_id": data.thread_id}},
        )
    except Exception:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Falló el agente, intenta de nuevo")
    return AskOut(respuesta=r["messages"][-1].content)
