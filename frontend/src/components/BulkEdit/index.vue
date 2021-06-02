<template>
  <div>
    <el-dialog :visible.sync="dialogFormVisible" width="60%" @close="closeDialog">
      <el-tabs ref="config-tabs" value="Config" @tab-click="handleSwitchTab">
        <el-tab-pane label="General" name="Config">General Settings
          <el-form label-position="left" label-width="90px" style="width: 80%; margin-left:50px; margin-top:20px">
            <el-form-item label="Hostname">
              <el-input v-model="hostname" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="WiFi" name="WiFi">RMT WiFi Client Configuration Settings
          <el-form :model="wifiSet" label-position="left" label-width="90px" style="width: 80%; margin-left:50px; margin-top:20px">
            <el-form-item>
              <el-checkbox v-model="sameAsAP" border @change="wifiToAp">Same as AP Server</el-checkbox>
            </el-form-item>
            <el-form-item label="SSID">
              <el-input v-model="wifiSet.ssid" maxlength="32" show-word-limit @input="wifiDiff" />
            </el-form-item>
            <el-form-item label="Password">
              <el-input v-model="wifiSet.password" show-password minlength="8" maxlength="32" @input="wifiDiff" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="Task" name="Task">Robot Task
          <el-form label-position="left" label-width="90px" style="width: 90%; margin-left:50px; margin-top:20px">
            <el-row class="target-header">
              <el-col :span="7"><span>Device ID</span></el-col>
              <el-col :span="7"><span>Hostname</span></el-col>
              <el-col :span="3"><span>Task</span></el-col>
              <el-checkbox v-model="sameAsFirst" border @change="TaskToFirst">same as first agent</el-checkbox>
            </el-row>
            <div v-for="device in deviceList" :key="device.DeviceID">
              <el-row style="margin-top:10px">
                <el-col :span="7"><span>{{ device.DeviceID }}</span></el-col>
                <el-col :span="7"><span>{{ device.Hostname }}</span></el-col>
                <el-select v-model="AgentCurrentTasks[device.DeviceID]" placeholder="Task" @change="handleSelect">
                  <el-option
                    v-for="item in device.task_list"
                    :key="item"
                    :label="item"
                    :value="item"
                  />
                </el-select>
              </el-row>
            </div>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      <div slot="footer" class="dialog-footer">
        <el-button v-waves @click="closeDialog">
          Close
        </el-button>
        <el-button v-waves :disabled="wifiSet.password.length<8" :loading="waitRequest" type="primary" @click="handleSubmit()">
          Submit
        </el-button>
      </div>
    </el-dialog>
  </div>

</template>

<script>
import { setConfigSame, setConfigDiff } from '@/api/robots'
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
      wifiSet: { 'ssid': '', 'password': '' },
      hostname: 'ROSCube',
      waitRequest: false,
      sameAsAP: true,
      sameAsFirst: false,
      currentTabName: 'Config',
      AgentCurrentTasks: {}
    }
  },
  watch: {
    dialogShow(val) {
      if (val) {
        this.sameAsAP = true
        this.wifiSet = Object.assign({}, this.tempWifi)
        this.deviceList.forEach((element) => {
          this.AgentCurrentTasks[element.DeviceID] = element.current_task
        })
      }
      this.sameAsFirst = false
      this.dialogFormVisible = val
    }
  },
  methods: {
    TaskToFirst(val) {
      if (val) {
        var idList = Object.keys(this.AgentCurrentTasks)
        idList.forEach((element) => {
          this.AgentCurrentTasks[element] = this.AgentCurrentTasks[idList[0]]
        })
      }
      this.$forceUpdate()
    },
    handleSwitchTab(val) {
      this.currentTabName = val.name
    },
    handleSelect() {
      this.sameAsFirst = false
      this.$forceUpdate()
    },
    closeDialog() {
      this.$emit('dialogShowChange', false)
    },
    wifiToAp(val) {
      if (val) {
        this.wifiSet = Object.assign({}, this.tempWifi)
      } else {
        this.wifiSet = { 'ssid': '', 'password': '' }
      }
    },
    wifiDiff() {
      this.sameAsAP = false
    },
    async handleSubmit() {
      this.waitRequest = true
      var tempData = {}
      if (this.currentTabName === 'Config') {
        tempData = { 'device_list': Array.from(this.deviceList, device => device.DeviceID.toString(10)),
          'config_dict': { 'hostname': this.hostname }}
        await setConfigSame(tempData)
        this.deviceList.forEach((element) => { element.Hostname = this.hostname })
      } else if (this.currentTabName === 'WiFi') {
        tempData = { 'device_list': Array.from(this.deviceList, device => device.DeviceID.toString(10)),
          'config_dict': { 'wifi': `${this.wifiSet.ssid} ${this.wifiSet.password}` }}
        await setConfigSame(tempData)
        this.tempWifi['ssid'] = this.wifiSet.ssid
        this.tempWifi['password'] = this.wifiSet.password
        this.$emit('syncData')
      } else if (this.currentTabName === 'Task') {
        tempData = { 'device_config_json': {}}
        this.deviceList.forEach((element) => {
          tempData['device_config_json'][element.DeviceID] = { 'task_mode': this.AgentCurrentTasks[element.DeviceID] }
        })
        await setConfigDiff(tempData)
        this.deviceList.forEach((element) => {
          element['current_task'] = this.AgentCurrentTasks[element.DeviceID]
        })
      }
      this.waitRequest = false
      this.$notify({
        title: 'Success',
        message: 'Configuration Update Successfully',
        type: 'success',
        duration: 2000
      })
    }
  }
}
</script>

<style>
.el-select {
  width: 200pt;
}
.el-col {
  margin-top: 10px;
}
.target-header {
  font-weight:bold;
  font-size:16px;
  margin-bottom: 20px;
}
</style>
