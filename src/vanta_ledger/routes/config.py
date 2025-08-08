from fastapi import APIRouter, Depends
from ..main import verify_token
from ..config import settings

router = APIRouter(prefix='/config', tags=['Config'])

@router.get('/')
async def get_config(current_user: dict = Depends(verify_token)):
    """
    Retrieve application configuration details and enabled feature flags for authenticated users.
    
    Returns:
        dict: A dictionary containing the application version and a set of enabled feature flags.
    """
    return {
        'version': settings.VERSION,
        'features': {
            'document_processing': True,
            'ocr': True,
            'ai_analysis': True,
            'file_upload': True
        }
    }
