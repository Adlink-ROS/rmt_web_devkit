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
            <div v-for="(device, key) in deviceList" :key="key">
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
            <el-carousel arrow="always" trigger="click" :autoplay="false" height="400px">
              <el-carousel-item>
                <el-row class="target-header" type="flex" align="middle" justify="center">
                  <el-col :span="5"><span>Device ID</span></el-col>
                  <el-col :span="5"><span>Interface Type</span></el-col>
                  <el-col :span="5"><span>IP Method</span></el-col>
                  <el-col :span="5"><span>Interface Name</span></el-col>
                </el-row>
                <div v-for="(device, key) in deviceList" :key="key">
                  <template v-if="interfaceName[device.DeviceID]">
                    <el-row type="flex" align="middle" justify="center" style="margin-top:10px">
                      <el-col :span="5"><span>{{ device.DeviceID }}</span></el-col>
                      <el-col :span="5"><span>{{ device.ipAddress[interfaceName[device.DeviceID]].deviceType }}</span></el-col>
                      <el-col :span="5"><span>{{ device.ipAddress[interfaceName[device.DeviceID]].ipMethod }}</span></el-col>
                      <el-col :span="5">
                        <el-select v-model="interfaceName[device.DeviceID]" style="width:100%">
                          <el-option
                            v-for="item in Object.keys(device.ipAddress)"
                            :key="item"
                            :label="item"
                            :value="item"
                          />
                        </el-select>
                      </el-col>
                    </el-row>
                  </template>
                </div>
              </el-carousel-item>
              <el-carousel-item>
                <el-row type="flex" align="middle" justify="center">
                  <el-radio v-model="ipMethod" label="auto">Automatic (DHCP)</el-radio>
                  <el-radio v-model="ipMethod" label="manual">Manual</el-radio>
                  <el-checkbox v-model="ipSequential" :disabled="ipMethod=='auto'" border @change="TaskToFirst">Sequential IP</el-checkbox>
                </el-row>
                <div v-for="(ipArray, key) in agentIp" :key="key">
                  <el-row class="ip-header" type="flex" justify="center">
                    <el-col :span="10"><span>{{ key }}</span></el-col>
                  </el-row>
                  <el-row type="flex" justify="center">
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
              </el-carousel-item>
            </el-carousel>
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
import { setConfigSame, setConfigDiff } from '@/api/robots'
import waves from '@/directive/waves' // waves directive
import agentItem from '../../mixins/agent'

export default {
  directives: { waves },
  mixins: [agentItem],
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
      sameAsAP: false,
      sameAsFirst: false,
      ipSequential: true,
      currentTabName: 'Config',
      AgentCurrentTasks: {},
      agentIp: {
        'IP Address': ['', '', '', ''],
        'Subnet Mask': ['', '', '', ''],
        'Gateway': ['', '', '', '']
      },
      ipMethod: 'auto',
      interfaceName: {}
    }
  },
  watch: {
    dialogShow(val) {
      this.sameAsFirst = false
      this.dialogFormVisible = val
    }
  },
  methods: {
    updateDevice() {
      this.deviceList.forEach((element) => {
        this.AgentCurrentTasks[element.DeviceID] = element.current_task
        this.interfaceName[element.DeviceID] = Object.keys(element.ipAddress)[0]
      })
    },
    clearConfig() {
      this.AgentCurrentTasks = {}
      this.interfaceName = {}
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
    SubmitSettingConfig() {
      var tempData = { 'device_list': Array.from(this.deviceList, device => device.DeviceID.toString(10)),
        'config_dict': { 'hostname': this.hostname }}

      setConfigSame(tempData).then(response => {
        if (this.responseVarify(response)) {
          this.deviceList.forEach((element) => { element.Hostname = this.hostname })
        }
        this.waitRequest = false
      })
    },
    SubmitSettingWifi() {
      var tempData = { 'device_list': Array.from(this.deviceList, device => device.DeviceID.toString(10)),
        'config_dict': { 'wifi': `${this.wifiSet.ssid} ${this.wifiSet.password}` }}

      setConfigSame(tempData).then(response => {
        if (this.responseVarify(response)) {
          this.deviceList.forEach((element) => {
            element['wifi'] = Object.assign({}, this.wifiSet)
          })
        }
        this.waitRequest = false
      })
    },
    SubmitSettingTask() {
      var tempData = { 'device_config_json': {}}

      this.deviceList.forEach((element) => {
        tempData['device_config_json'][element.DeviceID] = { 'task_mode': this.AgentCurrentTasks[element.DeviceID] }
      })
      setConfigDiff(tempData).then(response => {
        if (this.responseVarify(response)) {
          this.deviceList.forEach((element) => {
            element['current_task'] = this.AgentCurrentTasks[element.DeviceID]
          })
        }
        this.waitRequest = false
      })
    },
    SubmitSettingIp() {
      var tempData = { 'device_config_json': {}}
      var seqNumList = []
      var validGateway = ''

      if (this.ipMethod === 'manual') {
        const prefix = this.checkIpProperty(this.agentIp)

        if (!prefix) {
          this.$message({
            message: 'Invalid value of IPv4 Address',
            type: 'warning'
          })
          this.waitRequest = false
          return
        }

        if (!this.agentIp['Gateway'].every((element) => element === '') && this.checkIpAddress(this.agentIp, 'Gateway')) {
          validGateway = ` ${this.agentIp['Gateway'].join('.')}`
        }

        if (this.ipSequential) {
          this.deviceList.forEach((element, index) => {
            var seqNum = String(index + +this.agentIp['IP Address'][3])
            var sequentialIP = `${this.agentIp['IP Address'].slice(0, 3).join('.')}.${seqNum}`
            var configInput = `manual ${sequentialIP} ${prefix}` + validGateway
            tempData['device_config_json'][element.DeviceID] = {
              'ip_address': `${this.interfaceName[element.DeviceID]} ${configInput}`
            }
            seqNumList.push(seqNum)
          })
        } else {
          this.deviceList.forEach((element) => {
            var configInput = `manual ${this.agentIp['IP Address'].join('.')} ${prefix}` + validGateway
            tempData['device_config_json'][element.DeviceID] = {
              'ip_address': `${this.interfaceName[element.DeviceID]} ${configInput}`
            }
          })
        }

        setConfigDiff(tempData).then(response => {
          if (this.responseVarify(response)) {
            if (this.ipSequential) {
              this.deviceList.forEach((element, index) => {
                var seqIpArray = JSON.parse(JSON.stringify(this.agentIp))
                seqIpArray['IP Address'][3] = seqNumList[index]
                element['ipAddress'][this.interfaceName[element.DeviceID]] = Object.assign(
                  element['ipAddress'][this.interfaceName[element.DeviceID]], {
                    ipMethod: 'manual',
                    ipArray: seqIpArray
                  }
                )
              })
            } else {
              this.deviceList.forEach((element) => {
                element['ipAddress'][this.interfaceName[element.DeviceID]] = Object.assign(
                  element['ipAddress'][this.interfaceName[element.DeviceID]], {
                    ipMethod: 'manual',
                    ipArray: this.agentIp
                  }
                )
              })
            }
          }
          this.waitRequest = false
        })
      } else if (this.ipMethod === 'auto') {
        this.deviceList.forEach((element) => {
          tempData['device_config_json'][element.DeviceID] = {
            'ip_address': `${this.interfaceName[element.DeviceID]} auto`
          }
        })
        setConfigDiff(tempData).then(response => {
          if (this.responseVarify(response)) {
            this.deviceList.forEach((element) => {
              element['ipAddress'][this.interfaceName[element.DeviceID]] = Object.assign(
                element['ipAddress'][this.interfaceName[element.DeviceID]], {
                  ipMethod: 'auto',
                  ipArray: this.emptyAddress
                }
              )
            })
          }
          this.waitRequest = false
        })
      }
    },
    async handleSubmit() {
      this.waitRequest = true

      if (this.currentTabName === 'Config') {
        this.SubmitSettingConfig()
      } else if (this.currentTabName === 'WiFi') {
        this.SubmitSettingWifi()
      } else if (this.currentTabName === 'Task') {
        this.SubmitSettingTask()
      } else if (this.currentTabName === 'IPv4') {
        this.SubmitSettingIp()
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
