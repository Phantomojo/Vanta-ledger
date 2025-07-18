from fastapi import APIRouter
from ..paperless_integration import PaperlessIntegration

router = APIRouter(prefix="/system", tags=["system"])
paperless = PaperlessIntegration()

@router.get('/paperless_status')
def get_paperless_status():
    """
    Get Paperless-ngx system status and recent activity.
    """
    # Example: fetch stats from Paperless-ngx
    status = {'running': True}
    try:
        docs = paperless.get_documents(page=1, page_size=20)
        status['queued'] = sum(1 for d in docs if d.get('status') == 'queued')
        status['processing'] = sum(1 for d in docs if d.get('status') == 'processing')
        status['completed'] = sum(1 for d in docs if d.get('status') == 'done')
        status['failed'] = sum(1 for d in docs if d.get('status') == 'failed')
        status['recent'] = [
            {'id': d['id'], 'title': d['title'], 'status': d.get('status', 'unknown'), 'created': d.get('created', '')}
            for d in docs[:10]
        ]
    except Exception as e:
        status['running'] = False
        status['error'] = str(e)
    return status 