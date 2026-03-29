from fastapi import APIRouter

router = APIRouter(prefix='/trends', tags=['trends'])

@router.get('/')
def get_trends():
    return {'trends': []}
