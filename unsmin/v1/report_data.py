import os
import requests
import logging
import re
from flask_restful import Resource, Api
from flask.views import MethodView
from bs4 import BeautifulSoup
from flask import Blueprint, render_template, request
from .helper import make_request, get_params_values_from_html_page, display_data_parameters, \
    get_table_values_data, validating_data, validating_date, get_report_search_page_params
from unsmin.config import config_by_name
from .custom_exceptions import CustomException
from flask import current_app as app

config = config_by_name[os.environ['FLASK_ENV']]
login_url = config.LOGIN_URL
report_url = config.REPORT_URL
username = config.USERNAME
password = config.PASSWORD
pagination_search_count = config.PAGINATION_SEARCH_COUNT

report_data = Blueprint('report_data', __name__)
api = Api(report_data)


class ReportData(Resource):

    def get(self):
        # import pdb;pdb.set_trace()
        if request.args:
            search_mail = request.args.get('email')
            app.logger.info("request data email: {}".format(search_mail))

        if not request.args or not search_mail:
            return {"message": "invalid parameters"}, 400

        # request session
        session = requests.Session()
        try:
            # to get the hidden values in login page for making the payload for login request
            login_get_resp = make_request(session, login_url, "get")
            l_data = get_params_values_from_html_page(login_get_resp)
            l_data['dnn$ctr671$Login$Login_DNN$txtPassword'] = password
            l_data['dnn$ctr671$Login$Login_DNN$txtUsername'] = username
            l_data['ScriptManager'] = "dnn$ctr671$Login_UP|dnn$ctr671$Login$Login_DNN$cmdLogin"
            l_data['__ASYNCPOST'] = True

            login_post_resp = make_request(session, login_url, "post", l_data)
            report_get_resp = make_request(session, report_url, "get")
            bs_content = BeautifulSoup(report_get_resp.content, "html.parser")
            if bs_content.find("a", {"id": "dnn_ctr4088_Links_lstLinks_ReportIcon_0"}):
                raw_link = bs_content.find("a", {"id": "dnn_ctr4088_Links_lstLinks_ReportIcon_0"})['onclick']
                raw_links = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', raw_link)
            else:
                return CustomException("unable to process your request. Please try again", "500").to_dict()
            report_link = raw_links[0].split("'")[0]
            report_search_resp = make_request(session, report_link, "get")

            report_data = get_report_search_page_params(report_search_resp)
            rs_resp = make_request(session, report_link, "post", report_data)

            search_fields = get_report_search_page_params(rs_resp)
            search_fields["Scriptmanager1"] = "Scriptmanager1|ReportViewer1$ctl08$ctl00"
            search_fields["ReportViewer1$ctl08$ctl03$txtValue"] = search_mail
            search_fields["ReportViewer1$ctl08$ctl00"] = "View Report"
            search_fields["__EVENTTARGET"] = ""
            search_resp = make_request(session, report_link, "post", search_fields)

            search_data_fields = get_report_search_page_params(search_resp)
            search_data_fields["ReportViewer1$ctl09$ctl00$CurrentPage"] = ""
            search_data_fields["ReportViewer1$ctl09$ctl03$ctl00"] = ""
            search_data_fields["Scriptmanager1"] = "Scriptmanager1|ReportViewer1$ctl13$Reserved_AsyncLoadTarget"
            search_data_fields["__EVENTTARGET"] = "ReportViewer1$ctl13$Reserved_AsyncLoadTarget"
            search_data_fields["ReportViewer1$ctl08$ctl03$txtValue"] = search_mail
            search_data_fields["null"] = 100
            final_resp = make_request(session, report_link, "post", search_data_fields)

            final_content = BeautifulSoup(final_resp.content, "html.parser")

            all_rec = final_content.findAll('div', id=re.compile('72iT0R0x'))
            if not all_rec:
                return {"message": False}
            rec_source = [obj.text for obj in all_rec]
            all_course = final_content.findAll('div', id=re.compile('96iT0R0x'))
            course = [obj.text for obj in all_course]
            all_cer_date = final_content.findAll('div', id=re.compile('100iT0R0x'))
            certificate_date = [obj.text for obj in all_cer_date]

            l_val = [i for i in range(len(rec_source)) if rec_source[i].lower() == "online training"]
            for index_val in l_val:
                if course[index_val] == "BSAFE" and certificate_date[index_val]:
                    return {"message": True}
            return {"message": False}
        except Exception as e:
            app.logger.error(
                "Exception while processing the data for mail_id{} and exception: {}".format(request.args.get('email'),
                                                                                             str(e)))
            return CustomException("unable to process your request. Please try again", "500").to_dict()


api.add_resource(ReportData, '/v1/traveldata/report/isrecordfound')
