from fastapi import HTTPException

from schemas.camasir import MachineTypeSchema


def camasir_controller(request):
    try:
        if ((0<request.machine_count<3) and (request.machine_type == (MachineTypeSchema.NORMAL or MachineTypeSchema.DRYER))):
            return True
    except Exception as e:
         raise HTTPException(status_code=405, detail=" Not Allowed Parameters")

