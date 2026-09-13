from schemas.detection import VehicleDetection, Defect


def json_to_vehicle(data):

    defects = []

    for d in data["defects"]:

        defects.append(

            Defect(

                type=d["type"],
                confidence=d["confidence"],
                severity=d["severity"]

            )

        )

    return VehicleDetection(

        plate=data["plate"],
        brand=data["brand"],
        model=data["model"],
        year=data["year"],
        inspection_date=data["inspection_date"],
        defects=defects

    )