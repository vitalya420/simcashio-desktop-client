import json


class PayloadGenerator:
    def __init__(self, client_id):
        self.client_id = client_id

    def registration(self, email, pw, name, tel, ref):
        return json.dumps({
            "cmd51": {
                "ver": "0.501",
                "email": email,
                "pw": pw,
                "name": name,
                "tel": tel,
                "ref": ref
            }
        })

    def login(self, email, pw, sims):
        return json.dumps({
            "cmd53": {
                "clientid": self.client_id,
                "ver": "0.501",
                "aver": "9",
                "user": email,
                "pw": pw,
                "phone": "samsung galaxy s9",
                "wifi": "<unknown ssid>",
                "wifipwr": "3",
                "gps": "",
                "sims": [
                    sim.to_dict() for sim in sims
                ]}})

    def sms_received(self, sms_uuid, imsi):
        return json.dumps({"rsp01": {
            "clientid": self.client_id,
            "smss": [{
                "uuid": sms_uuid,
                "imsi": str(imsi)}]}})

    def sms_sent(self, sms_uuid, imsi):
        return json.dumps({"cmd59": {
            "smss": [{
                "uuid": sms_uuid,
                "imsi": str(imsi),
                "status": 1,
                "stime": 119,
                "dtime": 2294,
                "last": 1}],
            "clientid": self.client_id}})

    def change_sim(self, imsi, ISO, ph_code, price="0.00400000"):
        return json.dumps({"cmd54": {
            "clientid": self.client_id,
            "sims": [{
                "imsi": str(imsi),
                "desc": "",
                "action": "1",
                # "patterns":"[{\"ISO\":\"DEU\",\"pref\":\"+49\",\"price\":\"0.00500000\"}]",
                "patterns": "[{\"ISO\":\"" + ISO + "\",\"pref\":\"" + ph_code + "\",\"price\":\"" + price + "\"}]",
                "lim0": "Infinity",
                "lim1": "Infinity",
                "lim2": "Infinity",
                "lim3": "Infinity",
                "dlim0": "2020-10-05T17:45:00.000Z",
                "dlim1": "2020-10-05T23:59:00.000Z",
                "dlim2": "2020-10-07T23:59:00.000Z",
                "dlim3": "2020-11-03T23:59:00.000Z"}]}})

    def update_received(self):
        return json.dumps({"rsp05": {
            "status": 1,
            "clientid": self.client_id}})

    def update_balance_received(self):
        return json.dumps({"rsp04": {"status": 1, "clientid": self.client_id}})

    def update_request(self, email):
        return json.dumps({"cmd60": {
            "clientid": self.client_id,
            "email": email}})

    def pong(self):
        return json.dumps({"clientid": self.client_id})
