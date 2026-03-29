from fastapi import APIRouter

router = APIRouter(prefix='/action-plans', tags=['action-plans'])

@router.get('/')
def list_action_plans():
    return {'items': []}

@router.post('/')
def create_action_plan(payload: dict):
    return {'created': True, 'payload': payload}
