from fastapi import APIRouter

router = APIRouter(prefix='/quality-records', tags=['quality-records'])

@router.get('/')
def list_quality_records():
    return {'items': []}

@router.post('/')
def create_quality_record(payload: dict):
    return {'created': True, 'payload': payload}
