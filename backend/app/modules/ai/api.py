from fastapi import APIRouter, Depends
from app.modules.auth.dependencies import get_current_user
from app.modules.users.schema import UserResponse
from app.modules.ai.service import AiTaxService, AiChatRequest, AiChatResponse

router = APIRouter(tags=["AI Tax Assistant"])


@router.post("/tax-chat", response_model=AiChatResponse)
async def chat_with_tax_assistant(
    request: AiChatRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Interactive AI Tax Advisory Assistant based on Bangladesh Income Tax Act 2023."""
    return AiTaxService.get_tax_advice(request.prompt)
