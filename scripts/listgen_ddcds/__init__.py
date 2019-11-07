from flask_script import Command
from scripts.listgen_ddcds.listgen_full import FullListGeneration
from scripts.listgen_ddcds.listgen_delta import DeltaListGeneration
from scripts.common import ScriptLogger

logger = ScriptLogger('ddcds_list_generator').get_logger()


class ListGenerationFull(Command):

    def run(self):
        return FullListGeneration(logger=logger).generate_full_list()


class ListGenerationDelta(Command):

    def run(self):
        return DeltaListGeneration(logger=logger).generate_delta_list()
