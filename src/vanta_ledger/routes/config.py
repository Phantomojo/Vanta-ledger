from fastapi import APIRouter, Depends
from ..auth import AuthService
from ..config import settings

router = APIRouter(prefix='/config', tags=['Config'])

@router.get('/')
async def get_config(current_user: dict = Depends(AuthService.verify_token)):
    return {
        'version': settings.VERSION,
        'features': {
            'document_processing': True,
            'ocr': True,
            'ai_analysis': True,
            'file_upload': True
        }
    }
