from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pandas as pd
import requests
import os
import re
import time
from flask import current_app as app
month_to_numbers = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 'Jul': '07',\
                    'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}


def validating_date(date):
    d_format = "%Y%m%d"
    try:
        date = datetime.strptime(date, d_format)
        if date:
            return True
    except Exception as e:
        app.logger.error(
            "Exception while processing the date and Exception: {}".format(str(e)))
        return False


def date_formating(date, d_format):
    # date formate changed to dd-mm-yyyy and get the previous date
    new_f = "%d-%m-%Y"
    given_date = datetime.strptime(date, d_format).strftime(new_f)
    before_date = (datetime.strptime(date, d_format).date() - timedelta(days=1)).strftime(new_f)

    return given_date, before_date


def make_request(session=None, url=None, method="get", params={}, headers={}):
    try:
        if not session:
            session = requests.Session()
        start_time = time.time()
        if method and method.lower() == "post":
            response = session.post(url, params)
        else:
            response = session.get(url)
        app.logger.info("total time for connecting the url: {} Time: {}".format(url,time.time()-start_time))
    except Exception as e:
        app.logger.error("Exception While connecting to the url: {} and Error is: {}".format(url, e))
        response = {}
    return response


def get_params_values_from_html_page(response):
    bs_content = BeautifulSoup(response.content, "html.parser")

    data = {}
    data['__EVENTTARGET'] = "dnn$ctr671$Login$Login_DNN$cmdLogin"
    data['__EVENTARGUMENT'] = ""
    data['__VIEWSTATE'] = bs_content.find("input", {"name": "__VIEWSTATE"})["value"]
    data['__VIEWSTATEGENERATOR'] = bs_content.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"]
    data['__EVENTVALIDATION'] = bs_content.find("input", {"name": "__EVENTVALIDATION"})["value"]
    data['__dnnVariable'] = bs_content.find("input", {"name": "__dnnVariable"})["value"]
    data['__RequestVerificationToken'] = bs_content.find("input", {"name": "__RequestVerificationToken"})["value"]
    data['ScrollTop'] = 274

    return data


def get_val(content, f_val):
    # to get the values from span tag
    con = content.find('span', {'id': f_val})
    if con:
        if "dnn_ctr1237_ProfileXRay_gvTRList_lblTravel_" in f_val:
            travel_date = re.findall(r'\d{2}[-/][A-Za-z]{3}[-/]\d{4}', con.string.strip())[0]
            if travel_date:
                mon = travel_date.split("-")[1]
                mon_val = month_to_numbers[mon]
                travel_date = travel_date.replace(mon, mon_val)
            return travel_date

        return con.string.strip()


def get_table_values_data(content):
    column_names = ['Travel', 'ML', 'Submited', 'Status']
    df = pd.DataFrame(columns=column_names)

    for i in range(10):
        travel = 'dnn_ctr1237_ProfileXRay_gvTRList_lblTravel_' + str(i)
        ml = 'dnn_ctr1237_ProfileXRay_gvTRList_lblML_' + str(i)
        date = 'dnn_ctr1237_ProfileXRay_gvTRList_Label6_' + str(i)
        status = 'dnn_ctr1237_ProfileXRay_gvTRList_lblStatus_' + str(i)
        l = [travel, ml, date, status]

        # geting the values from table using beatifulsoup
        data = list(map(lambda val: get_val(content, val), l))
        if any(data):
            d_obj = {column_names[i]: data[i] for i in range(len(l))}
            df = df.append(d_obj, ignore_index=True)
    return df


def pagination_data_parameters(response):
    data = get_params_values_from_html_page(response)


def validating_data(df, name, date):
    d_format = "%Y%m%d"
    c_date, b_date = date_formating(date, d_format)
    df_values = df[((df['Status'] == 'Cleared') | (df['Status'] == 'Approved')) & (df['ML'].str.contains(name)) &
                   ((df['Travel'] == c_date) | (df['Travel'] == b_date))]

    return df_values


def display_data_parameters(p_list_data, search_mail):
    p_list_data['dnn$ctr1237$ProfileXRay$txtEmail'] = search_mail
    p_list_data['dnn$ctr1237$ProfileXRay$ddlAgency'] = 14
    p_list_data["dnn$dnnSEARCH$txtSearch"] = ""
    p_list_data["dnn$ctr1237$ProfileXRay$gvTRList$ctl01$txtTest"] = ""
    p_list_data["dnn$ctr1237$ProfileXRay$txtFirstName"] = ""
    p_list_data["dnn$ctr1237$ProfileXRay$txtLastName"] = ""
    p_list_data['dnn$ctr1237$ProfileXRay$gvUserList$ctl02$hfDeactivated'] = True
    p_list_data['dnn$ctr1237$ProfileXRay$gvUserList$ctl02$hfDeactivatedOn'] = ""
    p_list_data['dnn$ctr1237$ProfileXRay$gvUserList$ctl02$hfDeactivatedBy'] = "n/a"
    p_list_data['__EVENTTARGET'] = "dnn$ctr1237$ProfileXRay$gvUserList"
    p_list_data['__EVENTARGUMENT'] = "Select$0"
    p_list_data['__VIEWSTATEENCRYPTED'] = ""

    return p_list_data


def get_report_search_page_params(response):
    bs_content = BeautifulSoup(response.content, "html.parser")
    data = dict()
    data["Scriptmanager1"] = "UpdatePanel1|btnSimulate"
    data['__EVENTTARGET'] = "btnSimulate"
    data['__EVENTARGUMENT'] = ""
    data['__VIEWSTATE'] = bs_content.find("input", {"name": "__VIEWSTATE"})["value"]
    data['__VIEWSTATEGENERATOR'] = bs_content.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"]
    data['__EVENTVALIDATION'] = bs_content.find("input", {"name": "__EVENTVALIDATION"})["value"]
    data["ReportViewer1$ctl03$ctl00"] = ""
    data["ReportViewer1$ctl03$ctl01"] = ""
    data["ReportViewer1$isReportViewerInVs"] = ""
    data["ReportViewer1$ctl14"] = ""
    data["ReportViewer1$ctl15"] = "standards"
    data["ReportViewer1$AsyncWait$HiddenCancelField"] = False
    data["ReportViewer1$ToggleParam$store"] = ""
    data["ReportViewer1$ToggleParam$collapse"] = False
    data["ReportViewer1$ctl12$ClientClickedId"] = ""
    data["ReportViewer1$ctl11$store"] = ""
    data["ReportViewer1$ctl11$collapse"] = False
    data["ReportViewer1$ctl13$VisibilityState$ctl00"] = None
    data["ReportViewer1$ctl13$ScrollPosition"] = ""
    data["ReportViewer1$ctl13$ReportControl$ctl02"] = ""
    data["ReportViewer1$ctl13$ReportControl$ctl03"] = ""
    data["ReportViewer1$ctl13$ReportControl$ctl04"] = 100
    data["__ASYNCPOST"] = True
    return data
