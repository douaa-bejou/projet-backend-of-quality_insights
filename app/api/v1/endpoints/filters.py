from fastapi import APIRouter

router = APIRouter(prefix='/filters', tags=['filters'])

@router.post('/')
def apply_filters(payload: dict):
    return {'filtered': True, 'payload': payload}
