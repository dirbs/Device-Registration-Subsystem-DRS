from app.api.v1.models.association import ImeiAssociation
from scripts.listgen_ddcds import Helper


class DeltaListGeneration:

    @staticmethod
    def generate_delta_list():
        delta_list = []
        imeis = Helper.get_imeis()
        for i in imeis:
            if not i.get('exported') and i.get('end_date') is None:
                delta_list = Helper.add_to_list(delta_list, i, "ADD")
                ImeiAssociation.mark_exported(i.get('imei'), i.get('uid'))
            elif i.get('exported') and i.get('end_date'):
                if i.get('exported_at') < i.get('end_date'):
                    delta_list = Helper.add_to_list(delta_list, i, "REMOVE")
                    ImeiAssociation.update_export_date(i.get('imei'), i.get('uid'))
        if len(delta_list):
            Helper().upload_list(delta_list, "ddcds-delta-list")
            return "Job Done."
        else:
            return "List was empty"
