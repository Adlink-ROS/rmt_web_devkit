<template>
  <div>
    <el-dialog :visible.sync="dialogFormVisible" @close="closeDialog">
      <el-tabs value="Config">
        <el-tab-pane label="General" name="Config">General Settings
          <el-form ref="dataForm" label-position="left" label-width="90px" style="width: 400px; margin-left:50px; margin-top:20px">
            <el-form-item label="Hostname">
              <el-input v-model="hostname" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="WiFi" name="WiFi">RMT WiFi Client Configuration Settings
          <el-form ref="dataForm" :model="wifi_set" label-position="left" label-width="90px" style="width: 400px; margin-left:50px; margin-top:20px">
            <el-form-item>
              <el-checkbox v-model="sameAsAP" border @change="wifi_to_ap">Same as AP Server</el-checkbox>
            </el-form-item>
            <el-form-item label="SSID">
              <el-input v-model="wifi_set.ssid" maxlength="32" show-word-limit @input="wifi_diff" />
            </el-form-item>
            <el-form-item label="Password">
              <el-input v-model="wifi_set.password" show-password minlength="8" maxlength="32" @input="wifi_diff" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      <div slot="footer" class="dialog-footer">
        <el-button v-waves @click="closeDialog">
          Cancel
        </el-button>
        <el-button v-waves :disabled="wifi_set.password.length<8" :loading="wait_request" type="primary" @click="handleUpdate()">
          Confirm
        </el-button>
      </div>
    </el-dialog>
  </div>

</template>

<script>
import { set_config_same } from '@/api/robots'
import waves from '@/directive/waves' // waves directive

export default {
  directives: { waves },
  props: {
    dialogShow: {
      type: Boolean,
      default: false
    },
    deviceList: {
      type: Array,
      default: () => []
    },
    tempWifi: {
      type: Object,
      default: () => {}
    }
  },
  data() {
    return {
      dialogFormVisible: this.dialogShow,
      wifi_set: { 'ssid': '', 'password': '' },
      hostname: 'ROSCube',
      wait_request: false,
      sameAsAP: true
    }
  },
  watch: {
    dialogShow(val) {
      if (val) {
        this.sameAsAP = true
        this.wifi_set = Object.assign({}, this.tempWifi)
      }
      this.dialogFormVisible = val
    }
  },
  methods: {
    closeDialog() {
      this.$emit('dialogShowChange', false)
    },
    wifi_to_ap(val) {
      if (val) {
        this.wifi_set = Object.assign({}, this.tempWifi)
      } else {
        this.wifi_set = { 'ssid': '', 'password': '' }
      }
    },
    wifi_diff() {
      this.sameAsAP = false
    },
    async handleUpdate() {
      var temp_data = { 'device_list': Array.from(this.deviceList, device => device.DeviceID.toString(10)),
        'config_dict': { 'hostname': this.hostname, 'wifi': `${this.wifi_set.ssid} ${this.wifi_set.password}` }}
      this.wait_request = true
      await set_config_same(temp_data)
      this.tempWifi['ssid'] = this.wifi_set.ssid
      this.tempWifi['password'] = this.wifi_set.password
      this.deviceList.forEach((element) => { element.Hostname = this.hostname })
      this.wait_request = false
      this.$emit('dialogShowChange', false)
      this.$emit('syncData')
      this.$notify({
        title: 'Success',
        message: 'Update Successfully',
        type: 'success',
        duration: 2000
      })
    }
  }
}
</script>
