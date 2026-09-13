class LocationService:

    def get_location(
        self,
        defect_center_x,
        vehicle_x1,
        vehicle_x2
    ):
        """
        Détermine si le défaut est à gauche,
        au centre ou à droite de la voiture.
        """

        vehicle_width = vehicle_x2 - vehicle_x1

        # Position relative du défaut dans la voiture
        relative_x = (
            defect_center_x - vehicle_x1
        ) / vehicle_width

        if relative_x < 0.33:

            return "left"

        elif relative_x < 0.66:

            return "center"

        else:

            return "right"