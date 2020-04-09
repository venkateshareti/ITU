import os
import requests
import logging
from flask_restful import Resource, Api
from flask.views import MethodView
from bs4 import BeautifulSoup
from flask import Blueprint, render_template, request
from .helper import make_request, get_params_values_from_html_page, display_data_parameters, \
    get_table_values_data, validating_data, validating_date
from unsmin.config import config_by_name
from .custom_exceptions import CustomException
from flask import current_app as app

config = config_by_name[os.environ['FLASK_ENV']]
login_url = config.LOGIN_URL
profile_x_ray_url = config.PROFILE_X_RAY_URL
username = config.USERNAME
password = config.PASSWORD
pagination_search_count = config.PAGINATION_SEARCH_COUNT

data_search_and_access = Blueprint('data_search_and_access', __name__)
api = Api(data_search_and_access)


class DataSearchAndAccess(Resource):
    
    def get(self):
        if request.args:
            search_mail = request.args.get('email')
            date = request.args.get('date')
            app.logger.info("request data email: {} and date : {}".format(search_mail,date))

        if not request.args or not search_mail or not date:
            return {"message": "invalid parameters"}, 400

        date_validation = validating_date(date)
        if not date_validation:
            return {"message": "Invalid date/ date format should be yyyymmdd "},400
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
            profile_x_ray_get_reap = make_request(session, profile_x_ray_url, "get")

            # get the values from profile_x_ray_page
            p_data = get_params_values_from_html_page(profile_x_ray_get_reap)
            p_data['dnn$ctr1237$ProfileXRay$txtEmail'] = search_mail
            p_data['dnn$ctr1237$ProfileXRay$ddlAgency'] = 14
            p_data["dnn$dnnSEARCH$txtSearch"] = ""
            p_data["dnn$ctr1237$ProfileXRay$txtFirstName"] = ""
            p_data["dnn$ctr1237$ProfileXRay$txtLastName"] = ""
            p_data["dnn$ctr1237$ProfileXRay$btnSearchNewUser"] = "Processing ..."
            p_data['__EVENTTARGET'] = ""

            # making a request for search the profile with email
            profile_x_ray_search_post_resp = make_request(session, profile_x_ray_url, "post", p_data)
            for i in range(pagination_search_count):

                # extract the values form profile_x_ray page
                p_list_data = get_params_values_from_html_page(profile_x_ray_search_post_resp)

                # adding some more parameters
                p_list_data = display_data_parameters(p_list_data, search_mail=search_mail)

                # adding extra parameters to payload from 2nd request
                if i > 0:
                    p_list_data['__EVENTARGUMENT'] = "Page$" + str(i + 1)
                    p_list_data['__EVENTTARGET'] = "dnn$ctr1237$ProfileXRay$gvTRList"

                # making a request for display all values
                profile_x_ray_search_post_resp = make_request(session, profile_x_ray_url, "post", p_list_data)
                content = BeautifulSoup(profile_x_ray_search_post_resp.content, "html.parser")

                if not content.find("span", {"id": "dnn_ctr1237_ProfileXRay_gvUserList_lblName_0"}):
                    return {"message": "Unable to find the data with mailID {}".format(search_mail)}

                if i == 0 and content.find("span", {"id": "dnn_ctr1237_ProfileXRay_gvUserList_lblName_0"}):
                    name_obj = content.find("span", {"id": "dnn_ctr1237_ProfileXRay_gvUserList_lblName_0"}).string.strip()
                    name = name_obj.split(' ')[-1]

                # to display the table values in dataframe form
                df = get_table_values_data(content)
                # search the name and date value
                final_value = validating_data(df, name, date)

                if len(final_value) > 0:
                    return {"message": True}
                if not content.find("tr", {"class": "gvDefault_PagerStyle"}):
                    return {"message": False}
                if len(df) < 10:
                    return {"message": False}

        except Exception as e:
            app.logger.error("Exception while processing the data for mail_id{} and exception: {}".format(request.args.get('email'),str(e)))
            return CustomException("unable to process your request. Please try again", "500").to_dict()


api.add_resource(DataSearchAndAccess, '/v1/traveldata/isrecordfound')
