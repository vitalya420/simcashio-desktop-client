from base64 import b64decode, b64encode
from random import randint

import uuid


class SIM:
    def __init__(self, imsi, imei, carrier="Vodafone UA"):
        self.carrier = carrier
        self.imsi = imsi
        self.imei = imei

    def to_dict(self):
        return {
            "imsi": self.imsi,
            "imei": self.imei,
            "simtel": "",
            "carrier": self.carrier,
            "pver": 0
        }


class Utils:

    @staticmethod
    def generate_sims(amount: int) -> list:
        sims = []
        for _ in range(amount):
            sims.append(SIM(Utils.random_imsi("255"), Utils.random_imei()))
        return sims

    @staticmethod
    def random_imei() -> str:
        def checksum(number, alphabet='0123456789'):
            n = len(alphabet)
            number = tuple(alphabet.index(i)
                           for i in reversed(str(number)))
            return (sum(number[::2]) +
                    sum(sum(divmod(i * 2, n))
                        for i in number[1::2])) % n

        def calc_check_digit(number, alphabet='0123456789'):
            check_digit = checksum(number + alphabet[0])
            return alphabet[-check_digit]

        start = str(randint(10000000, 99999999))
        imei = start
        while len(imei) < 14:
            imei += str(randint(0, 9))
        imei += calc_check_digit(imei)
        return imei

    @staticmethod
    def random_uuid() -> str:
        return "cccc" + str(uuid.uuid4())[4:]

    @staticmethod
    def random_imsi(mc="255") -> str:
        return f"{mc}0{randint(10000000000, 99999999999)}"

    @staticmethod
    def split_payload(shit: str) -> tuple:
        decoded = b64decode(shit)
        vector = decoded[:16]
        payload = decoded[16:]
        return payload, vector

    @staticmethod
    def final_payload(encrypted_payload: tuple) -> str:
        encrypted_msg, iv = encrypted_payload
        payload = b64decode(encrypted_msg)
        shit = b64decode("AfQAAA==")
        result = iv + payload + shit
        print(result)
        return result
