from graph.state import DefectraState

from tools.vehicle_tools import VehicleTools
from tools.history_tools import HistoryTools


class VehicleHistoryAgent:

    def __init__(self):

        self.vehicle_tools = VehicleTools()

        self.history_tools = HistoryTools()

    def execute(self, state: DefectraState):

        vehicle = self.vehicle_tools.get_vehicle_by_plate(
            state["plate"]
        )

        if vehicle is None:

            state["answer"] = "Véhicule introuvable."

            return state

        state["vehicle"] = vehicle

        inspection = self.history_tools.get_last_inspection(
            vehicle.id
        )

        state["inspection"] = inspection

        return state

    def close(self):

        self.vehicle_tools.close()

        self.history_tools.close()