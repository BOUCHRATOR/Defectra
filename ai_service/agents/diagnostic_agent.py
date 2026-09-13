from graph.state import DefectraState

from tools.defect_tools import DefectTools


class DiagnosticAgent:

    def __init__(self):

        self.defect_tools = DefectTools()

    def execute(self, state: DefectraState):

        # Si aucune inspection n'existe,
        # il n'y a aucun défaut à récupérer.
        if state["inspection"] is None:

            state["defects"] = []

            return state

        defects = self.defect_tools.get_defects(

            state["inspection"].id

        )

        state["defects"] = defects

        return state

    def close(self):

        self.defect_tools.close()