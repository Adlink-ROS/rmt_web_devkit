from typing import Dict
from fastapi.testclient import TestClient
from app.core.config import settings
from .test_wifi import str_generator
import os
import pytest
import subprocess
import random
import time

@pytest.fixture(scope="module", autouse=True)
def agent_start_id():
    return random.randint(0,500)

@pytest.fixture(scope="module", autouse=True)
def generate_agent(agent_start_id):
    subprocess.run(["sudo", "killall", "agent_example"])
    num = random.randint(1,10)
    process = subprocess.Popen(["sudo", "python3", "multi_agents.py", "-n", str(num), "-s", str(agent_start_id)])
    time.sleep(2)
    yield num
    subprocess.run(["sudo", "killall", "agent_example"])

class TestRobotPage:
    @pytest.fixture(scope="class", autouse=True)
    def get_robot_list(self, client: TestClient, superuser_token_headers: Dict[str, str]):
        response = client.get(
            "/robots/discovery", headers=superuser_token_headers)
        return response

    @pytest.fixture(scope="class", autouse=True)
    def agent_data(self, get_robot_list):
        return get_robot_list.json()["data"]

    def test_status_code(self, get_robot_list):
        assert get_robot_list.status_code == 200

    def test_robot_data(self, agent_data, generate_agent):
        assert agent_data["total"] == generate_agent
        if generate_agent:
            for agent in agent_data["items"]:
                for feature in agent:
                    assert agent[feature]

class TestGetConfig:
    @pytest.fixture(scope="class", autouse=True)
    def default_config_data(self):
        return {"config_list": ["cpu", "ram", "hostname", "wifi"]}

    @pytest.fixture(scope="class", autouse=True)
    def faux_config_data(self, agent_start_id):
        return {"device_list": [str(agent_start_id+20)], "config_list": ["cpu", "ram", "hostname", "wifi"]}

    @pytest.fixture(scope="class", autouse=True)
    def get_config_all(self, client: TestClient, superuser_token_headers: Dict[str, str], default_config_data):
        response = client.post(
            "/robots/get_config_for_all", headers=superuser_token_headers, json=default_config_data)
        return response

    @pytest.fixture(scope="class", autouse=True)
    def agent_data(self, get_config_all):
        return get_config_all.json()["data"]

    def test_status_code(self, get_config_all):
        assert get_config_all.status_code == 200

    def test_config_data(self, agent_data, generate_agent):
        assert len(agent_data) == generate_agent
        for agent in agent_data:
            assert agent

    def test_config_id(self, client: TestClient, superuser_token_headers: Dict[str, str], agent_start_id, generate_agent):
        config_data = {"device_list": [],"config_list": ["cpu","ram","hostname","wifi"]}
        for id in range(agent_start_id, agent_start_id+generate_agent):
            config_data["device_list"].append(str(id))
            response = client.post(
                f"/robots/get_same_config_by_id", headers=superuser_token_headers, json=config_data)
            assert response.status_code == 200
    
    def test_faux_id(self, client: TestClient, superuser_token_headers: Dict[str, str], agent_start_id, faux_config_data):
        response = client.post(
            f"/robots/get_same_config_by_id", headers=superuser_token_headers, json=faux_config_data)
        with pytest.raises(AssertionError):
            assert response.json()["code"] == 20000
    
class TestSetConfig:
    @pytest.fixture(scope="function", autouse=True)
    def set_config_data(self):
        return {"device_list": [],"config_dict": {"hostname": str_generator(size=random.randint(1, 32)), "locate": "off"}}

    @pytest.fixture(scope="function", autouse=True)
    def set_config_data_id(self):
        return {"device_config_json": {}}

    def test_same_config(self, client: TestClient, superuser_token_headers: Dict[str, str], agent_start_id, generate_agent, set_config_data):
        for id in range(agent_start_id, agent_start_id+generate_agent):
            set_config_data["device_list"].append(str(id))
            response = client.put(
                "/robots/set_same_config_by_id", headers=superuser_token_headers, json=set_config_data)
            assert response.json()["code"] == 20000
    
    def test_diff_config(self, client: TestClient, superuser_token_headers: Dict[str, str], agent_start_id, generate_agent, set_config_data_id):
        for id in range(agent_start_id, agent_start_id+generate_agent):
            set_config_data_id["device_config_json"][str(id)] = {"hostname": str_generator(size=random.randint(1, 32)), "locate": "off"}
            response = client.put(
                "/robots/set_diff_config_by_id", headers=superuser_token_headers, json=set_config_data_id)
            assert response.json()["code"] == 20000

    def test_faux_same_config(self, client: TestClient, superuser_token_headers: Dict[str, str], agent_start_id, set_config_data):
        set_config_data["device_list"].append(str(agent_start_id+20))
        response = client.put(
                "/robots/set_same_config_by_id", headers=superuser_token_headers, json=set_config_data)
        with pytest.raises(AssertionError):
            assert response.json()["code"] == 20000
    
    def test_faux_diff_config(self, client: TestClient, superuser_token_headers: Dict[str, str], agent_start_id, set_config_data_id):
        set_config_data_id["device_config_json"][str(agent_start_id+20)] = {"hostname": str_generator(size=random.randint(1, 32)), "locate": "off"}
        response = client.put(
            "/robots/set_diff_config_by_id", headers=superuser_token_headers, json=set_config_data_id)
        with pytest.raises(AssertionError):
            assert response.json()["code"] == 20000