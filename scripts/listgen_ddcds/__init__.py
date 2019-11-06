from flask_script import Command
from scripts.listgen_ddcds.listgen_full import FullListGeneration
from scripts.listgen_ddcds.listgen_delta import DeltaListGeneration


class ListGenerationFull(Command):

    def run(self):
        return FullListGeneration.generate_full_list()


class ListGenerationDelta(Command):

    def run(self):
        return DeltaListGeneration.generate_delta_list()
