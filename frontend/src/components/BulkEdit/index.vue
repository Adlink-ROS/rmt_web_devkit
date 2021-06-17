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
              <el-checkbox v-model="sameAsFirst" border @change="TaskToFirst">apply the first to all</el-checkbox>
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
        <el-tab-pane label="IPv4" name="IPv4">IPv4 Address
          <el-form label-position="left" label-width="90px" style="width: 90%; margin-left:50px; margin-top:20px">
            <el-row>
              <el-radio v-model="ipMethod" label="auto">Automatic (DHCP)</el-radio>
              <el-radio v-model="ipMethod" label="manual">Manual</el-radio>
              <el-checkbox v-model="ipSequential" :disabled="ipMethod=='auto'" border @change="TaskToFirst">Sequential IP</el-checkbox>
            </el-row>
            <div v-for="(ipArray, key) in agentIp" :key="key">
              <el-row class="ip-header">
                <el-col :span="4"><span>{{ key }}</span></el-col>
              </el-row>
              <el-row>
                <el-input
                  v-for="(segment, index) in ipArray"
                  :key="index"
                  v-model="ipArray[index]"
                  maxlength="3"
                  :disabled="ipMethod=='auto'"
                  style="width: 10%"
                />
              </el-row>
            </div>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      <div slot="footer" class="dialog-footer">
        <el-button v-waves @click="closeDialog">
          Close
        </el-button>
        <el-button v-waves :loading="waitRequest" type="primary" @click="handleSubmit()">
          Submit
        </el-button>
      </div>
    </el-dialog>
  </div>

</template>

<script>
import { setConfigSame, setConfigDiff, setConfigSequential, responseVarify } from '@/api/robots'
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
      ipSequential: true,
      currentTabName: 'Config',
      AgentCurrentTasks: {},
      agentIp: {
        'IP Address': ['', '', '', ''],
        'Subnet Mask': ['', '', '', ''],
        'Gateway': ['', '', '', '']
      },
      ipMethod: 'auto'
    }
  },
  watch: {
    dialogShow(val) {
      this.AgentCurrentTasks = Object.assign({}, {})
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
    checkAllProperty() {
      if (!this.checkIpAddress('IP Address') || !this.checkIpAddress('Subnet Mask')) {
        return false
      } else if (!this.agentIp['Gateway'].every((element) => element === '') && !this.checkIpAddress('Gateway')) {
        return false
      }
      var bitcode = this.agentIp['Subnet Mask'].reduce((total, current) => {
        return total + Number(current).toString(2).padStart(8, '0')
      }, '')

      if (bitcode.split('01').length >= 2) {
        return false
      }
      const prefix = bitcode.split('1').length - 1

      return prefix
    },
    checkIpAddress(ipArray) {
      var ipCheck = this.agentIp[ipArray].join('.')
      return (/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(ipCheck))
    },
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
        this.wifiSet = Object.assign(this.wifiSet, this.tempWifi)
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
        setConfigSame(tempData).then(response => {
          if (responseVarify(response)) {
            this.deviceList.forEach((element) => { element.Hostname = this.hostname })
          }
          this.waitRequest = false
        })
      } else if (this.currentTabName === 'WiFi') {
        tempData = { 'device_list': Array.from(this.deviceList, device => device.DeviceID.toString(10)),
          'config_dict': { 'wifi': `${this.wifiSet.ssid} ${this.wifiSet.password}` }}
        setConfigSame(tempData).then(response => {
          if (responseVarify(response)) {
            this.tempWifi['ssid'] = this.wifiSet.ssid
            this.tempWifi['password'] = this.wifiSet.password
            this.$emit('syncData', this.currentTabName)
          }
          this.waitRequest = false
        })
      } else if (this.currentTabName === 'Task') {
        tempData = { 'device_config_json': {}}
        this.deviceList.forEach((element) => {
          tempData['device_config_json'][element.DeviceID] = { 'task_mode': this.AgentCurrentTasks[element.DeviceID] }
        })
        setConfigDiff(tempData).then(response => {
          if (responseVarify(response)) {
            this.deviceList.forEach((element) => {
              element['current_task'] = this.AgentCurrentTasks[element.DeviceID]
            })
          }
          this.waitRequest = false
        })
      } else if (this.currentTabName === 'IPv4') {
        if (this.ipMethod === 'manual') {
          const prefix = this.checkAllProperty()
          if (!prefix) {
            this.$message({
              message: 'Invalid value of IPv4 Address',
              type: 'warning'
            })
            this.waitRequest = false
            return
          }
          tempData = { 'device_list': Array.from(this.deviceList, device => device.DeviceID.toString(10)) }
          var configInput = `manual ${this.agentIp['IP Address'].join('.')} ${prefix}`
          if (!this.agentIp['Gateway'].every((element) => element === '') && this.checkIpAddress('Gateway')) {
            configInput = configInput + ' ' + this.agentIp['Gateway'].join('.')
          }
          if (this.ipSequential) {
            tempData['numbering_config_start'] = { 'ip_address': configInput }
            setConfigSequential(tempData).then(response => {
              if (responseVarify(response)) {
                Object.assign(this.tempWifi, {
                  'ipMethod': 'manual',
                  'ipArray': this.agentIp
                })
                this.$emit('syncData', 'IPv4Seq')
              }
              this.waitRequest = false
            })
          } else {
            tempData['config_dict'] = { 'ip_address': configInput }
            setConfigSame(tempData).then(response => {
              if (responseVarify(response)) {
                Object.assign(this.tempWifi, {
                  'ipMethod': 'manual',
                  'ipArray': this.agentIp
                })
                this.$emit('syncData', this.currentTabName)
              }
              this.waitRequest = false
            })
          }
        } else if (this.ipMethod === 'auto') {
          tempData = { 'device_list': Array.from(this.deviceList, device => device.DeviceID.toString(10)),
            'config_dict': { 'ip_address': 'auto' }}
          setConfigSame(tempData).then(response => {
            if (responseVarify(response)) {
              Object.assign(this.tempWifi, {
                'ipMethod': 'auto',
                'ipArray': {
                  'IP Address': Array(4).fill(''),
                  'Subnet Mask': Array(4).fill(''),
                  'Gateway': Array(4).fill('')
                }
              })
              this.$emit('syncData', this.currentTabName)
            }
            this.waitRequest = false
          })
        }
      }
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
.ip-header {
  font-weight:bold;
  font-size:16px;
  margin-top: 20px;
  margin-bottom: 10px;
}
</style>
