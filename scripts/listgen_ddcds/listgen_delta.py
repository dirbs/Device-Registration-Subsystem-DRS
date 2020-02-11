import sys
from app.api.v1.models.association import ImeiAssociation
from scripts.listgen_ddcds.helper import Helper


class DeltaListGeneration:

    def __init__(self, logger):
        """Constructor"""
        self.logger = logger

    def generate_delta_list(self):
        try:
            delta_list = []
            imeis = Helper(self.logger).get_imeis()
            self.logger.info("Adding IMEIs to list and marking them as exported...")
            for i in imeis:
                if not i.get('exported') and i.get('end_date') is None:
                    delta_list = Helper(self.logger).add_to_delta_list(delta_list, i, "add")
                    ImeiAssociation.mark_exported(i.get('id'))
                elif i.get('exported') and i.get('end_date'):
                    if i.get('exported_at') < i.get('end_date'):
                        delta_list = Helper(self.logger).add_to_delta_list(delta_list, i, "remove")
                        ImeiAssociation.update_export_date(i.get('id'))
            self.logger.info("Checking if generated list contains IMEIs...")
            if len(delta_list):
                Helper(self.logger).upload_list(delta_list, "ddcds-delta-list")
                self.logger.info("List has been generated and uploaded successfully.")
                self.logger.info("exiting...")
                sys.exit(0)
            else:
                self.logger.info("No IMEI to be exported")
                self.logger.info("exiting...")
                sys.exit(0)
        except Exception as e:
            self.logger.exception("Exception occurred", e)
            sys.exit(0)
