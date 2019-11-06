import sys
from app.api.v1.models.association import ImeiAssociation
from scripts.listgen_ddcds import Helper


class FullListGeneration:

    @staticmethod
    def generate_full_list():
        try:
            full_list = []
            imeis = Helper.get_imeis()
            for i in imeis:
                if not i.get('exported') and i.get('end_date') is None:
                    full_list = Helper.add_to_list(full_list, i, "ADD")
                    ImeiAssociation.mark_exported(i.get('imei'), i.get('uid'))
            if len(full_list):
                Helper().upload_list(full_list, "ddcds-full-list")
                Helper().logger.info("Job Done.")
                sys.exit(0)
            else:
                Helper().logger.info("No IMEI to be exported")
                Helper().logger.info("exiting...")
                sys.exit(0)
        except Exception as e:
            Helper().logger.exception("Exception occurred", e)
            sys.exit(0)

