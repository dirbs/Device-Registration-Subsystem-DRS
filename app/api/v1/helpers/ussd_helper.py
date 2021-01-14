class Ussd_helper:
    @staticmethod
    def set_args_dict_for_regdetails(arguments, user_data):
        data = {}

        data.update({'user_id': user_data['user_id']})
        data.update({'user_name': arguments['cnic']})
        data.update({'cnic': arguments['cnic']})
        data.update({'msisdn': arguments['msisdn']})
        data.update({'network': arguments['network']})
        data.update({'device_count': arguments['device_count']})
        data.update({'imei_per_device': str(len(arguments['imeis'][0]))})
        data.update({'import_type': "USSD"})
        data.update({'imeis': arguments['imeis']})
        data.update({'m_location': "local"})
        # data.update({'processing_status': "ask yasir"})
        # data.update({'report_status': "ask yasir"})
        # data.update({'summary': "ask yasir"})
        # data.update({'report': "ask yasir"})
        data.update({'status': 1})

        if 'password' in user_data:
            # print("this is new user")
            # data.update({'user_id': user_data['user_id']})
            data.update({'username': user_data['cnic']})
            data.update({'password': user_data['password']})

        return data

    @staticmethod
    def set_args_dict_for_devicedetails(reg_response, arguments, gsma_response):
        data = {}

        data.update({'reg_id': reg_response.id})
        data.update({'reg_details_id': reg_response.id})
        data.update({'id': reg_response.id})
        data.update({'user_id': arguments['user_id']})
        data.update({'brand': gsma_response["gsma"]["brand_name"]})
        data.update({'model_name': gsma_response["gsma"]["model_name"]})
        data.update({'operating_system': gsma_response["gsma"]["operating_system"]})
        data.update({'model_num': ""})
        data.update({'device_type': gsma_response["gsma"]["device_type"]})
        data.update({'technologies': gsma_response["gsma"]["bands"]})
        return data

    @staticmethod
    def set_count_message(msisdn_all_counts):
        message = "Total devices applied:"+str(msisdn_all_counts['count_with_msisdn']) + ". Total review count: "\
                  +str(msisdn_all_counts['review_count']) + ". Total pending review count: "\
                  +str(msisdn_all_counts['pending_review_count']) + ". Total approved count: "\
                  +str(msisdn_all_counts['approved_count']) + ". Total rejected count: "\
                  +str(msisdn_all_counts['rejected_count']) + ". Total failed count: "\
                  +str(msisdn_all_counts['failed_count']) + "."

        return message


    @staticmethod
    def set_message_for_user_info(status):
        return {
            1: 'Your device has been put for registration. You will be notified accordingly.',
            2: 'Your device has been registered and waiting for documents.',
            3: 'Your device has been registered and is waiting for review.',
            4: 'Your device is in review. You will be notified shortly.',
            5: 'Your device is in Information Request condition.',
            6: 'Your device has been approved.',
            7: 'Your device has been rejected.',
            8: 'Your application has been closed.',
            9: 'Your request has been failed. Please try again later.',
            10: 'Your application has been processed.',
            11: 'Your device is in the processing phase'

        }.get(status, "Status Not Found")


    @staticmethod
    def set_record_info(device_info):
        import ast
        # set IMEIS string
        imeis_dict = ast.literal_eval(device_info.imeis)
        imeis = imeis_dict[0]
        if len(imeis) > 1:
            str_imeis = ','.join(str(e) for e in imeis)
        else:
            str_imeis = imeis

        # set status string
        status = Ussd_helper.set_message_for_user_info(device_info.status)

        string_message = "Device id: " + str(device_info.id) + ", User name: " + device_info.user_name + \
                         ", Device IMEIS: " + str(str_imeis) + " Registered at: " + str(device_info.created_at) + " and Status: " + status
        return string_message

    @staticmethod
    def return_operator_token(network):
        return {
            'zong': 'em9uZzoxMjM=',
            'ufone': 'dWZvbmU6MTIz',
            'telenor': 'dGVsZW5vcjoxMjM=',
            'jazz': 'amF6ejoxMjM='

        }.get(network, 'Zm9vOmJhcg==')

