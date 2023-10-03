import requests
import time
import json
import random

import os


HOST_URL = os.environ.get("HOST_URL", None)

if HOST_URL is None:
    raise Exception("HOST_URL environment variable is not set")

ENDPOINT = HOST_URL + "/e/ingest/events/v1"
API_TOKEN = os.environ.get("API_TOKEN", None)
if API_TOKEN is None:
    raise Exception("API_TOKEN environment variable is not set")

def publish_event(e_name, e_payload):

    url = ENDPOINT
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(API_TOKEN)
    }
    e_data = {"name": e_name, "payload": e_payload}
    try:
        resp = requests.post(url, data=json.dumps(e_data), headers=headers, timeout=1.0)
        if resp.status_code != 200:
            print("Error: {} - {}".format(resp.status_code, resp.text))
        else:
            print("Event published successfully")
    except Exception as e:
        print(str(e))

def payments_events():

    tnx_id_range = range(20000, 2500000)
    user_id_range = range(20000, 2500000)
    amount_range = range(0, 5000)
    bank_name_choices = ["AmEX", "Citi", "National Bank"]

    t_id = "a_" + str(random.choice(tnx_id_range))
    u_id = "u_" + str(random.choice(user_id_range))
    amount = random.choice(amount_range)
    bank_name = random.choice(bank_name_choices)
    time.sleep(0.1)
    publish_event(
        "payment_data_collected",
        {"payment_id": t_id, "amount": amount, "user_id": u_id},
    )
    time.sleep(0.1)
    publish_event(
        "bank_api_called",
        {"payment_id": t_id, "bank_name": bank_name, "channel_type": "online"},
    )
    tnx_status_p = random.choice(range(0, 100))
    if tnx_status_p <= 90:
        tnx_status_code = 200
        tnx_status = "success"
    elif (tnx_status_p > 90) & (tnx_status_p < 99):
        tnx_status_code = random.choice([400, 401, 404, 501])
        tnx_status = "fail"
    else:
        return None
    time.sleep(0.1)
    publish_event(
        "bank_response_receive",
        {
            "payment_id": t_id,
            "bank_name": bank_name,
            "response_status": tnx_status,
            "response_status_code": tnx_status_code,
            "user_id": u_id,
        },
    )
    if tnx_status == "fail":
        time.sleep(0.1)
        publish_event(
            "reverse_payment_initiated",
            {"payment_id": t_id, "user_id": u_id, "amount": amount},
        )
    else:
        time.sleep(0.1)
        publish_event(
            "ledger_updated",
            {"payment_id": t_id, "user_id": u_id, "ledger_status": "updated"},
        )
        time.sleep(0.1)
        publish_event(
            "invoice_generated",
            {"invoice_id": "inv9876", "payment_id": t_id, "user_id": u_id},
        )
        if tnx_status_p != 61:
            time.sleep(0.1)
            publish_event(
                "email_sent",
                {
                    "email_id": "user@drdroid.io",
                    "user_id": u_id,
                    "payment_id": t_id,
                },
            )
    return None

while 1:
    payments_events()
    time.sleep(30)