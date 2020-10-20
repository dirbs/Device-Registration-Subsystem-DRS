import numpy as np
import requests
import json
import re # re.findall() finds the required data in string, we will find the digits in strings


class MultiSimCheck:

    @staticmethod
    def validate_imeis_capacity(core_base_url, api_version, imeis_list):
        # api_version validation
        api_version_small = api_version.lower()
        if not api_version_small == 'api/v2':
            return {"msg": "API Version V2 is required"}
        api_response = []
        api_response.append(True)
        # each device IMEIs list and operations over it
        for device_imeis_rec in imeis_list:
            device_imeis = device_imeis_rec[0].split(',')

            # take imeis count to check for match in imeiquantitysupport, simslot and (removable_euicc,
            # nonremovable_euicc, removable_euicc, removable_uicc)
            imeis_count = str(len(device_imeis))
            ind_device_imeis = []

            # consider device imeis, fetch the tacs and make them unique
            for single_imei in device_imeis:
                ind_device_imeis.append(single_imei[0:8])

            # make the TACs unique
            device_unique_list = np.unique(np.array(ind_device_imeis))
            device_having_multiple_tacs = len(device_unique_list)
            same_model = []  # initiate same model list

            # loop through the TACs for each device. scenario-> a single device can have multiple TACs
            for tac in device_unique_list:
                str_imeis = " "

                # get GSMA record against each TAC and match them with IMEIs count given in list
                gsma_response = requests.get(core_base_url + api_version_small + '/tac/' + str(tac)).json()

                if gsma_response["gsma"] is None:
                    same_model.append("Nill")
                    api_response.append({"gsma_tac_response": "No record found for TAC:" + str(tac)})
                    api_response[0] = "False"
                else:
                    # make model list for similar model in case of multiple TACs for a single device instance
                    same_model.append(gsma_response["gsma"]["model_name"])

                    # check against simslots
                    sim_slots = gsma_response["gsma"]["simslot"].lower()
                    if not sim_slots == "not known":
                        # check if simslot matches with imeis_count
                        if not str(sim_slots) == imeis_count:
                            api_response.append({"simslot_mismatch": "GSMA record for TAC: " + str(
                                tac) + " shows: " + str(sim_slots) + " count, Provided IMEIs: " + str_imeis.join(
                                device_imeis) + " are: " + str(imeis_count)})
                            api_response[0] = "False"
                    else:  # if simslot is Not Known
                        imeiquantitysupport = gsma_response["gsma"]["imeiquantitysupport"].lower()
                        if not imeiquantitysupport == "not known":
                            # check if simslot matches with imeis_count
                            if not sim_slots == imeis_count:
                                api_response.append({"imeiquantitysupport_mismatch": "GSMA record for TAC: " + str(
                                    tac) + " shows: " + str(
                                    imeiquantitysupport) + " count, Provided IMEIs: " + str_imeis.join(
                                    device_imeis) + " are: " + str(imeis_count)})
                                api_response[0] = "False"
                        else:  # if simslot and imeiquantitysupport are Not Known
                            nonremovable_euicc = gsma_response["gsma"]["nonremovable_euicc"]
                            nonremovable_uicc = gsma_response["gsma"]["nonremovable_uicc"]
                            removable_euicc = gsma_response["gsma"]["removable_euicc"]
                            removable_uicc = gsma_response["gsma"]["removable_uicc"]
                            # get the digits part out of the string
                            nonremovable_euicc = list(map(int, re.findall(r'\d+', nonremovable_euicc)))
                            nonremovable_uicc = list(map(int, re.findall(r'\d+', nonremovable_uicc)))
                            removable_euicc = list(map(int, re.findall(r'\d+', removable_euicc)))
                            removable_uicc = list(map(int, re.findall(r'\d+', removable_uicc)))
                            if nonremovable_euicc:
                                int_nonremovable_euicc = nonremovable_euicc[0]
                            else:
                                int_nonremovable_euicc = 0
                            if nonremovable_uicc:
                                int_nonremovable_uicc = nonremovable_uicc[0]
                            else:
                                int_nonremovable_uicc = 0
                            if removable_euicc:
                                int_removable_euicc = removable_euicc[0]
                            else:
                                int_removable_euicc = 0
                            if removable_uicc:
                                int_removable_uicc = removable_uicc[0]
                            else:
                                int_removable_uicc = 0
                            total_sim_capacity = sum((
                                                     int_nonremovable_euicc, int_nonremovable_uicc, int_removable_euicc,
                                                     int_removable_uicc))
                            # combo_euicc_uicc = [None]
                            combo_euicc_uicc = str(total_sim_capacity)
                            # get the total sim capacity and check it with the number of device_imeis and
                            if total_sim_capacity > 0:
                                if combo_euicc_uicc == imeis_count:
                                    pass  # condition met
                                else:
                                    if not int(imeis_count) == int(combo_euicc_uicc):
                                        api_response.append({"combo_euicc_uicc_mismatch": "GSMA record for TAC: " + str(
                                            tac) + " shows: " + str(
                                            combo_euicc_uicc) + " count, Provided IMEIs: " + str_imeis.join(
                                            device_imeis) + " are: " + str(imeis_count)})
                                        api_response[0] = "False"
                                    pass
                            else:
                                if int(imeis_count) > 2:
                                    api_response.append({"combo_euicc_uicc_mismatch": "GSMA record for TAC: " + str(
                                        tac) + " shows: " + str(
                                        combo_euicc_uicc) + " count, Provided IMEIs: " + str_imeis.join(
                                        device_imeis) + " are: " + str(imeis_count)})
                                    api_response[0] = "False"
                                else:
                                    pass

            unique_model_list = np.unique(np.array(same_model))
            unique_model_list_len = len(device_unique_list)

            if int(unique_model_list_len) > 1:
                string_model_list = " & "
                api_response.append({"same_model_mismatch": "Provided IMEIs: " + str_imeis.join(
                    device_imeis) + " are not of the same model. GSMA models for provided IMEIs are: (" + string_model_list.join(
                    unique_model_list) + ")"})
                api_response[0] = "False"

        return (api_response)