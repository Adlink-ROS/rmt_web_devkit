from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv
from app import models, schemas
import gi

gi.require_version("NM", "1.0")
from gi.repository import GLib, NM
import sys, uuid

router = APIRouter()

@cbv(router)
class network_client():
    def __init__(self):
        self.main_loop = GLib.MainLoop()
        self.client = NM.Client.new(None)
        self.response = {}

    def create_profile(self, ssid, password, band):
        profile = NM.SimpleConnection.new()
        s_con = NM.SettingConnection.new()
        s_con.set_property(NM.SETTING_CONNECTION_ID, "RMTHost")
        s_con.set_property(NM.SETTING_CONNECTION_UUID, str(uuid.uuid4()))
        s_con.set_property(NM.SETTING_CONNECTION_TYPE, "802-11-wireless")
        s_con.set_property(NM.SETTING_CONNECTION_AUTOCONNECT, False)

        s_wireless = NM.SettingWireless.new()
        s_wireless.set_property(NM.SETTING_WIRELESS_SSID, GLib.Bytes.new(ssid.encode('utf-8')))
        s_wireless.set_property(NM.SETTING_WIRELESS_MODE, "ap")
        s_wireless.set_property(NM.SETTING_WIRELESS_BAND, band)

        s_secure = NM.SettingWirelessSecurity.new()
        s_secure.set_property(NM.SETTING_WIRELESS_SECURITY_KEY_MGMT, "wpa-psk")
        s_secure.set_property(NM.SETTING_WIRELESS_SECURITY_PSK, password)

        s_ip4 = NM.SettingIP4Config.new()
        s_ip4.set_property(NM.SETTING_IP_CONFIG_METHOD, NM.SETTING_IP4_CONFIG_METHOD_SHARED)

        profile.add_setting(s_con)
        profile.add_setting(s_ip4)
        profile.add_setting(s_wireless)
        profile.add_setting(s_secure)

        return profile

    def modify_cb(self, remote_con, result, data):
        if not remote_con.commit_changes_finish(result):
            callback_log = "Error: Failed to modify connection"
            self.response["modify"] = "-1"
        else:
            callback_log = "Connection successfully modified"
            self.response["modify"] = "0"
        print(callback_log)
        self.main_loop.quit()

    def active_cb(self, client, result, data):
        if not client.activate_connection_finish(result):
            callback_log = "Error: Failed to activate connection"
            self.response["active"] = "-1"
        else:
            callback_log = "Connection successfully activate"
            self.response["active"] = "0"
        print(callback_log)
        self.main_loop.quit()

    def deactive_cb(self, client, result, data):
        if not client.deactivate_connection_finish(result):
            callback_log = "Error: Failed to deactivate connection"
            self.response["deactive"] = "-1"
        else:
            callback_log = "Connection successfully deactivate"
            self.response["deactive"] = "0"
        print(callback_log)
        self.main_loop.quit()

    def added_cb(self, client, result, data):
        try:
            client.add_connection_finish(result)
            callback_log = "The connection profile has been successfully added to NetworkManager"
            self.response["create"] = "0"
        except Exception as e:
            callback_log = f"Error: {e}\n"
            self.response["create"] = "-1"
        print(callback_log)
        self.main_loop.quit()

    def got_secret(self, remote_con, result, data):
        secrets = remote_con.get_secrets_finish(result)
        if secrets:
            if not remote_con.update_secrets("802-11-wireless-security", secrets):
                print("Error updating secrets")
        self.main_loop.quit()

    def wifi_ap_init(self):
        con = self.create_profile("RMTserver", "adlinkros", "bg")
        self.client.add_connection_async(con, False, None, self.added_cb, None)
        self.main_loop.run()
    
    @router.get("/get_wifi_hotspot", response_model=schemas.Response, summary="Get WiFi hotspot settings on host server")
    def get_wifi_hotspot_mode(self):
        if not self.client.get_connection_by_id("RMTHost"):
            self.wifi_ap_init()
        remote_con = self.client.get_connection_by_id("RMTHost")
        remote_con.get_secrets_async("802-11-wireless-security", None, self.got_secret, None)
        self.main_loop.run()

        s_sec = remote_con.get_setting_wireless_security()
        s_wireless = remote_con.get_setting_wireless()

        password = s_sec.get_psk()
        ssid = NM.utils_ssid_to_utf8(s_wireless.get_ssid().get_data())
        band = s_wireless.get_band()
        hotspot_enable = False
        active_list = self.client.get_active_connections()
        for a_con in active_list:
            if a_con.get_id() == "RMTHost":
                active = True
        band_code = {"bg": "2.4 GHz", "a": "5 GHz"}
        band_freq = band_code[band]
        wifi_data = {
            "hotspot_enable": hotspot_enable,
            "ssid": ssid,
            "password": password,
            "band": band_freq
        }

        return {"code": 20000, "data": wifi_data}

    @router.post("/set_wifi_hotspot", response_model=schemas.Response, summary="Enable WiFi Hotspot on host server")
    def set_wifi_hotspot_mode(self, wifi_mode: schemas.WifiMode):
        if not self.client.get_connection_by_id("RMTHost"):
            self.wifi_ap_init()

        wifi_set = {
            "hotspot_enable": wifi_mode.hotspot_enable, 
            "ssid": wifi_mode.ssid, 
            "password": wifi_mode.password, 
            "band": wifi_mode.band
        }

        band_code = {"2.4 GHz": "bg", "5 GHz": "a"}

        if len(wifi_set["password"]) < 8 or len(wifi_set["password"]) > 32:
            raise HTTPException(status_code=400, detail="Invalid property: Password")
        if not wifi_set["ssid"] or len(wifi_set["ssid"]) > 32:
            raise HTTPException(status_code=400, detail="Invalid property: SSID")
        if wifi_set["band"] not in band_code:
            raise HTTPException(status_code=400, detail="Invalid property: Band")
        
        new_con = self.create_profile(wifi_set["ssid"], wifi_set["password"], band_code[wifi_set["band"]])
        remote_con = self.client.get_connection_by_id("RMTHost")
        remote_con.replace_settings_from_connection(new_con)
        remote_con.commit_changes_async(True, None, self.modify_cb, None)
        self.main_loop.run()
        active_list = self.client.get_active_connections()
        active_con = None

        for a_con in active_list:
            if a_con.get_id() == "RMTHost":
                active_con = a_con
        
        if wifi_set["hotspot_enable"] and not active_con:
            self.client.activate_connection_async(remote_con, None, None, None, self.active_cb, None)
            self.main_loop.run()
        elif not wifi_set["hotspot_enable"] and active_con:
            self.client.deactivate_connection_async(active_con, None, self.deactive_cb, None)
            self.main_loop.run()

        return {"code": 20000, "data": self.response}
