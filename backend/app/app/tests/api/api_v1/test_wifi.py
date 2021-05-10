from typing import Dict
from fastapi.testclient import TestClient
from app.core.config import settings
import os
import pytest
import subprocess
import string
import random

def str_generator(size, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@pytest.fixture(scope="module")
def default_wifi_data():
    return {"hotspot_enable": False,
            "ssid": "RMTserver",
            "password": "adlinkros",
            "band": "2.4 GHz"}

class TestWifiGetRequest:
    @pytest.fixture(scope="class", autouse=True)
    def get_wifi_set(self, client: TestClient, superuser_token_headers: Dict[str, str]):
        response = client.get(
            "/robots/get_wifi_hotspot", headers=superuser_token_headers)
        return response

    @pytest.fixture(scope="class", autouse=True)
    def user_data(self, get_wifi_set):
        return get_wifi_set.json()["data"]

    def test_status_code(self, get_wifi_set):
        assert get_wifi_set.status_code == 200

    @pytest.mark.parametrize("config_name", ["password", "ssid", "band"])
    def test_wifi_pwd(self, user_data, config_name):
        assert user_data[config_name]

    def test_default_wifi(self, client: TestClient, superuser_token_headers: Dict[str, str], default_wifi_data):
        if "RMTHost.nmconnection" in os.listdir("/etc/NetworkManager/system-connections"):
            subprocess.run(["nmcli", "con", "delete", "RMTHost"], stdout=subprocess.PIPE)
        response = client.get(
            "/robots/get_wifi_hotspot", headers=superuser_token_headers)
        assert response.json()["data"] == default_wifi_data

class TestWifiPostRequest:
    @pytest.fixture(scope="class", params=[(33,100,8,32), (1,32,0,7), (1,32,33,100)], ids=["ssid_over","pwd_short","pwd_over"])
    def faux_response(self, request, client: TestClient, superuser_token_headers: Dict[str, str], default_wifi_data):
        faux_set = {"ssid": str_generator(size=random.randint(request.param[0], request.param[1])),
                    "password": str_generator(size=random.randint(request.param[2], request.param[3])),
                    "band": "2.4 GHz",
                    "hotspot_enable": False}
        response = client.post("/robots/set_wifi_hotspot", headers=superuser_token_headers, json=faux_set)
        yield response
        subprocess.run(["nmcli", "con", "delete", "RMTHost"], stdout=subprocess.PIPE)
        response = client.post("/robots/set_wifi_hotspot", headers=superuser_token_headers, json=default_wifi_data)

    @pytest.fixture(scope="class", params=[True, False], ids=["init","exist"])
    def post_response(self, request, client: TestClient, superuser_token_headers: Dict[str, str]):
        if "RMTHost.nmconnection" in os.listdir("/etc/NetworkManager/system-connections") and request.param:
            subprocess.run(["nmcli", "con", "delete", "RMTHost"], stdout=subprocess.PIPE)
        test_set = {"ssid": str_generator(size=random.randint(1, 32)),
                    "password": str_generator(size=random.randint(8, 32)),
                    "band": "2.4 GHz",
                    "hotspot_enable": request.param}
        response = client.post("/robots/set_wifi_hotspot", headers=superuser_token_headers, json=test_set)
        return response

    def test_post_wifi(self, post_response): 
        assert post_response.status_code == 200
        assert "Error" not in post_response.json()["data"]

    def test_post_faux(self, faux_response):
        print(faux_response.json())
        with pytest.raises(AssertionError):
            assert faux_response.status_code == 200
