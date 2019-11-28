import sys
from app.api.v1.models.association import ImeiAssociation
from scripts.listgen_ddcds.helper import Helper


class FullListGeneration:

    def __init__(self, logger):
        """Constructor"""
        self.logger = logger

    def generate_full_list(self):
        try:
            full_list = []
            imeis = Helper(self.logger).get_imeis()
            self.logger.info("Adding IMEIs to list and marking them as exported...")
            for i in imeis:
                if i.get('end_date') is None:
                    full_list = Helper(self.logger).add_to_full_list(full_list, i)
                    ImeiAssociation.mark_exported(i.get('id'))
            self.logger.info("Checking if generated list contains IMEIs...")
            if len(full_list):
                Helper(self.logger).upload_list(full_list, "ddcds-full-list")
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

