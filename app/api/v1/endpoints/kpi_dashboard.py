from fastapi import APIRouter

router = APIRouter(prefix='/kpis', tags=['kpis'])

@router.get('/')
def get_kpis():
    return {'kpis': []}
