from .helper import Helper
from app.api.v1.models.association import ImeiAssociation


class FullListGeneration:

    @staticmethod
    def generate_full_list():
        full_list = []
        imeis = Helper.get_imeis()
        for i in imeis:
            if not i.get('exported') and i.get('end_date') is None:
                full_list = Helper.add_to_list(full_list, i, "ADD")
                ImeiAssociation.mark_exported(i.get('imei'), i.get('uid'))
        if len(full_list):
            Helper().upload_list(full_list, "first-full-list")
            return "Job Done."
        else:
            return "List was empty"
