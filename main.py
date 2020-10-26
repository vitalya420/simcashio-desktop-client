import json
import threading
import time
from pprint import pprint
import logging
from threading import Thread

import socketio

from AESTools import AESTools
from PayloadGenerator import PayloadGenerator
from Utils import Utils


# logging.basicConfig(level=logging.INFO)


class SimcashClient:
    def __init__(self, email=None, password=None, sim_amount=2):
        self.email = email
        self.password = password

        self.sims = Utils.generate_sims(sim_amount)
        self.sms_counter = 0
        self.last_balance = None
        self.last_update = None

        self.cipher = AESTools("uoy7Nj3Ya4P9eDdWXzJepQ==".encode())
        self.payload = PayloadGenerator(Utils.random_uuid())
        self.sio = socketio.Client()

        self._register_events()
        self._connect()

    def start(self):
        payload = self.cipher.encrypt(self.payload.login(self.email, self.password, self.sims))
        final = Utils.final_payload(payload)
        self.sio.emit("login", final)

    def register(self, email: str, password: str, name: str, tel: str, ref: str):
        payload = self.payload.registration(email, password, name, tel, ref)
        encrypted = self.cipher.encrypt(payload)
        final = Utils.final_payload(encrypted)
        self.sio.emit("register", final)

    def connect(self):
        print("Connected to simcash.io. SID:", self.sio.sid)

    def disconnect(self):
        print("Disconnected to simcash.io.")
        print("Reconnecting..")
        self.start()

    def register_result(self, data):
        final_data = json.loads(self.cipher.decrypt(*Utils.split_payload(data)))
        print(final_data)

    def login_result(self, data):
        final_data = json.loads(self.cipher.decrypt(*Utils.split_payload(data)))
        try:
            print(f"Balance: {final_data['rsp53']['bal3']}")
            print(final_data['rsp53']['recap'])
            # Starting pong thread.
            threading.Thread(target=self.ponging).start()
            self.sio.sleep(5)
            # Updating email
            payload = self.cipher.encrypt(self.payload.update_request(self.email))
            final = Utils.final_payload(payload)
            self.sio.emit("update_request", final)
            self.sio.sleep(5)
            for sim in self.sims:
                print(f"Updating sim imsi: {sim.imsi}")
                payload = self.cipher.encrypt(self.payload.change_sim(sim.imsi, "UKR", "+380", "0.00400000"))
                final = Utils.final_payload(payload)
                self.sio.emit("change_sim", final)
        except Exception as exc:
            print(f"Logging exception: {exc}")

    def send_sms(self, data):
        final_data = json.loads(self.cipher.decrypt(*Utils.split_payload(data)))
        pprint(final_data)
        sms_uuid, imsi = final_data['cmd01']['smss'][0]['uuid'], final_data['cmd01']['smss'][0]['imsi']
        received_payload = self.cipher.encrypt(self.payload.sms_received(sms_uuid, imsi))
        self.sio.emit("sms_received", Utils.final_payload(received_payload))
        sent_payload = self.cipher.encrypt(self.payload.sms_sent(sms_uuid, imsi))
        self.sio.emit("sms_sent", Utils.final_payload(sent_payload))
        print(f'Total message sent: {self.sms_counter + 1}')
        self.sms_counter += 1

    def update_data(self, data):
        final_data = json.loads(self.cipher.decrypt(*Utils.split_payload(data)))
        print(final_data)
        try:
            if final_data['cmd05']['bal3'] != self.last_balance:
                print(f"Balance: {final_data['cmd05']['bal3']}.")
                self.last_balance = final_data['cmd05']['bal3']
        except Exception as exc:
            print("Update data Exception", exc)
        payload = self.cipher.encrypt(self.payload.update_received())
        self.sio.emit("update_received", json.dumps({"_placeholder": True, "num": 0}))

    def change_sim_result(self, data):
        final_data = json.loads(self.cipher.decrypt(*Utils.split_payload(data)))
        print("Change sim result:", final_data['rsp54']['msg'])

    def update_balance(self, data):
        final_data = json.loads(self.cipher.decrypt(*Utils.split_payload(data)))
        if final_data['cmd04']['recap'] != self.last_update:
            print(final_data['cmd04']['recap'])
            self.last_update = final_data['cmd04']['recap']
        self.sio.emit("update_balance_received", Utils.final_payload(
            self.cipher.encrypt(
                self.payload.update_balance_received())))

    def ping(self, data):
        print("Прилетел пинг:", self.cipher.decrypt(*Utils.split_payload(data)))
        self.sio.emit("Pong", json.dumps({"_placeholder": True, "num": 0}))

    def ponging(self):
        while 1:
            # self.sio.emit("ping", Utils.final_payload(self.cipher.encrypt(self.payload.pong())))
            # self.sio.emit("Pong", Utils.final_payload(self.cipher.encrypt(self.payload.pong())))
            # self.sio.emit("Pong", Utils.final_payload(self.cipher.encrypt(self.payload.pong())))
            self.sio.emit("Pong", json.dumps({"_placeholder": True, "num": 0}))
            time.sleep(60)

    def register_event(self, func):
        self.sio.event(func)

    def _connect(self):
        self.sio.connect('https://secure.simcash.io',
                         headers={"User-Agent": "okhttp/4.9.0", 'X-Token': ''})

    def _register_events(self):
        self.sio.event(self.connect)
        self.sio.event(self.disconnect)
        self.sio.event(self.register_result)
        self.sio.event(self.login_result)
        self.sio.event(self.send_sms)
        self.sio.event(self.update_data)
        self.sio.event(self.change_sim_result)
        self.sio.event(self.update_balance)


if __name__ == "__main__":
    client = SimcashClient("segece2501@iazhy.com", "1", 1)
    client.start()
