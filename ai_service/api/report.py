from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.postgres import get_db
from services.report_service import ReportService

router = APIRouter(
    prefix="/report",
    tags=["Report"]
)


@router.post("/{inspection_id}")
def generate_report(
    inspection_id: int,
    db: Session = Depends(get_db)
):
    print()
    print("======================================")
    print("FASTAPI - GENERATION RAPPORT")
    print("======================================")
    print("Inspection ID :", inspection_id)

    try:
        service = ReportService(db)

        result = service.generate_report(
            inspection_id
        )

        print()
        print("===== RAPPORT GENERE =====")
        print(result)
        print("======================================")

        return result

    except Exception as e:

        import traceback

        print()
        print("!!!!!!!! ERREUR REPORT SERVICE !!!!!!!!")
        print(str(e))

        traceback.print_exc()

        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )