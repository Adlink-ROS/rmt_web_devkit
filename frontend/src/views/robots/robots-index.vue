<template>
  <div class="app-container">

    <div class="filter-container">
      <el-button v-waves class="filter-item" type="primary" @click="getList()">
        <svg-icon icon-class="radar" style="margin-right: 5px" />
        Scan
      </el-button>
      <el-button v-waves class="filter-item" type="primary" icon="el-icon-refresh" style="width: 110px" @click="deviceList=[]">
        Clear
      </el-button>
      <el-button v-waves class="filter-item" type="primary" icon="fas el-icon-fa-wifi" @click="dialogShowWifi(true)">
        WiFi mode
      </el-button>
      <el-button v-show="multipleSelection.length" v-waves class="filter-item" type="primary" icon="fas el-icon-fa-edit" @click="dialogShowGroup(true)">
        Bulk Edit
      </el-button>
    </div>

    <el-table
      ref="multipleTable"
      :key="tableKey"
      v-loading="listLoading"
      :default-sort="{prop: 'DeviceID', order: 'ascending'}"
      :data="deviceList"
      stripe
      fit
      highlight-current-row
      style="width: 100%;"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" align="center" width="45" />
      <el-table-column label="No." type="index" align="center" width="45" />
      <el-table-column label="Device ID" prop="DeviceID" sortable :sort-orders="['ascending', 'descending']" width="130px" align="center">
        <template #default="{row}">
          <span>{{ row.DeviceID }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Hostname" width="130px" align="center">
        <template #default="{row}">
          <span>{{ row.Hostname }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Model" width="110px" align="center">
        <template #default="{row}">
          <span>{{ row.Model }}</span>
        </template>
      </el-table-column>
      <el-table-column label="IP address" width="130px" align="center">
        <template #default="{row}">
          <span>{{ row.IP }}</span>
        </template>
      </el-table-column>
      <el-table-column label="MAC address" width="150px" align="center">
        <template #default="{row}">
          <span>{{ row.MAC }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Actions" align="center" width="150" class-name="small-padding fixed-width">
        <template #default="{row}">
          <el-tooltip effect="light" content="Configuration setting">
            <el-button v-waves icon="fas el-icon-fa-wrench" type="info" size="mini" @click="handleUpdate(row)" />
          </el-tooltip>
          <el-tooltip effect="light" content="Hardware I/O control">
            <el-button v-waves type="primary" size="mini" @click="handlecontrol(row)">
              Control
            </el-button>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column label="Task" align="center" width="140" class-name="small-padding fixed-width">
        <template #default="{row}">
          <el-select :value="row.current_task" placeholder="Task" :loading="listLoading" style="width: 100%" @change="handleTask($event, row)">
            <el-option
              v-for="item in row.task_list"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="pageSetting.page" :limit.sync="pageSetting.limit" @pagination="getList" />

    <el-dialog title="Edit Configuration" :visible.sync="editPanelSwitch">
      <el-tabs :value="defaultTabName">
        <el-tab-pane label="General" name="Config">General Settings
          <el-form ref="dataForm" :model="temp" label-position="left" label-width="90px" style="width: 400px; margin-left:50px; margin-top:20px">
            <el-form-item label="Hostname">
              <el-input v-model="temp.Hostname" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane v-if="temp.wifi" label="WiFi" name="WiFi">RMT WiFi Client Configuration Settings
          <el-form ref="dataForm" :model="temp" label-position="left" label-width="90px" style="width: 400px; margin-left:50px; margin-top:20px">
            <el-form-item>
              <el-checkbox v-model="sameAsAP" border @change="wifiToAp">Same as AP Server</el-checkbox>
            </el-form-item>
            <el-form-item label="SSID">
              <el-input v-model="temp.wifi.ssid" maxlength="32" show-word-limit @input="wifiDiff" />
            </el-form-item>
            <el-form-item label="Password">
              <el-input v-model="temp.wifi.password" show-password minlength="8" maxlength="32" @input="wifiDiff" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane v-if="temp.ipAddress" label="IPv4" name="IPv4">IPv4 Address
          <el-form label-position="left" label-width="90px" style="width: 90%; margin-left:50px; margin-top:20px">
            <el-row type="flex" align="middle" :gutter="20" style="font-size:16px;">
              <el-col :span="8">
                <el-select v-model="interfaceName" style="width:90%">
                  <el-option
                    v-for="item in Object.keys(temp.ipAddress)"
                    :key="item"
                    :label="item"
                    :value="item"
                  />
                </el-select>
              </el-col>
              <el-col :span="15"><span>Interface Type: {{ deviceTypeFilter(temp.ipAddress[interfaceName].deviceType) }}</span></el-col>
            </el-row>
            <el-row style="margin-top:20px">
              <el-radio v-model="temp.ipAddress[interfaceName].ipMethod" label="auto">Automatic (DHCP)</el-radio>
              <el-radio v-model="temp.ipAddress[interfaceName].ipMethod" label="manual">Manual</el-radio>
            </el-row>
            <div v-for="(ipArray, key) in temp.ipAddress[interfaceName].ipArray" :key="key">
              <el-row class="ip-header">
                <el-col :span="5"><span>{{ key }}</span></el-col>
              </el-row>
              <el-row>
                <el-input
                  v-for="(segment, index) in ipArray"
                  :key="index"
                  v-model="ipArray[index]"
                  maxlength="3"
                  :disabled="temp.ipAddress[interfaceName].ipMethod=='auto'"
                  style="width: 12%"
                />
              </el-row>
            </div>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      <div slot="footer" class="dialog-footer">
        <el-button v-waves @click="editPanelSwitch = false">
          Cancel
        </el-button>
        <el-button v-waves :loading="waitRequest" type="primary" @click="updateData()">
          Submit
        </el-button>
      </div>
    </el-dialog>
    <control-component
      :dialog-show="controlPanelSwitch"
      :config="temp"
      :locate="locateList[temp.Index-1]"
      @dialogShowChange="dialogShowControl"
      @syncData="syncLocate"
    />
    <wifi-mode-component
      :dialog-show="wifiPanelSwitch"
      :wifi-set="tempWifi"
      @dialogShowChange="dialogShowWifi"
      @syncData="syncWifi"
    />
    <bulk-edit-component
      ref="bulkEdit"
      :dialog-show="bulkPanelSwitch"
      :device-list="multipleSelection"
      :temp-wifi="tempWifi"
      @dialogShowChange="dialogShowGroup"
    />
  </div>
</template>

<script>
import { fetchRobotList, setConfigDiff, getConfigAll, fetchWifi } from '@/api/robots'
import agentItem from './mixins/agent'
import waves from '@/directive/waves' // waves directive
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import ControlComponent from './components/ControlPanel'
import WifiModeComponent from './components/WiFiMode'
import BulkEditComponent from './components/BulkEdit'

export default {
  name: 'ComplexTable',
  components: { Pagination, ControlComponent, WifiModeComponent, BulkEditComponent },
  directives: { waves },
  mixins: [agentItem],
  data() {
    return {
      tableKey: 0,
      deviceList: [],
      total: 0,
      multipleSelection: [],
      sameAsAP: false,
      listLoading: true,
      waitRequest: false,
      pageSetting: {
        page: 1,
        limit: 20
      },
      wifiSet: {},
      tempWifi: {},
      temp: {},
      locateList: [],
      bulkPanelSwitch: false,
      editPanelSwitch: false,
      controlPanelSwitch: false,
      wifiPanelSwitch: false,
      defaultTabName: 'Config',
      interfaceName: ''
    }
  },
  created() {
    fetchWifi().then(response => {
      this.wifiSet = response.data
    })
      .then(this.getList())
  },
  methods: {
    getList() {
      this.listLoading = true
      var config = { 'config_list': ['ip_address', 'task_list', 'task_mode', 'wifi'] }

      fetchRobotList()
        .then(response => {
          this.deviceList = response.data.items
          this.total = response.data.total
          this.locateList = Array(this.total).fill('off')
        })
        .then(() => getConfigAll(config))
        .then(response => {
          for (const [agentID, configItem] of Object.entries(response.data)) {
            var listIndex = this.deviceList.findIndex(agent => agent.DeviceID === agentID)
            var splitWifiString = configItem.wifi.split(' ')
            this.deviceList[listIndex]['ipAddress'] = {}
            configItem['ip_address']
              .split('#')
              .forEach((element) => {
                var tempSplit = element.split(' ')
                this.interfaceName = tempSplit[0]
                this.deviceList[listIndex]['ipAddress'][tempSplit[0]] = {
                  deviceType: tempSplit[1],
                  ipMethod: tempSplit[2],
                  ipArray: this.emptyAddress
                }
                if (tempSplit[2] === 'manual') {
                  this.deviceList[listIndex]['ipAddress'][tempSplit[0]]['ipArray'] = {
                    'IP Address': tempSplit[3].split('.'),
                    'Subnet Mask': this.cidrToSubnet(tempSplit[4]),
                    'Gateway': (tempSplit.length > 5) ? tempSplit[5].split('.') : Array(4).fill('')
                  }
                }
              })
            var splitTaskString = configItem.task_list.split(' ')
            this.deviceList[listIndex]['wifi'] = { 'ssid': splitWifiString[1], 'password': splitWifiString[3] }
            this.deviceList[listIndex]['task_list'] = splitTaskString
            this.deviceList[listIndex]['current_task'] = configItem.task_mode
          }
          this.listLoading = false
        })
    },

    // Handle agents selection in table
    handleSelectionChange(val) {
      this.multipleSelection = val
    },

    // Function for control component
    handlecontrol(row) {
      this.temp = Object.assign({}, row) // copy obj
      this.controlPanelSwitch = true
    },
    syncLocate(val) {
      this.locateList[this.temp.Index - 1] = val
    },
    dialogShowControl(val) {
      this.controlPanelSwitch = val
    },

    // Function for wifi ap mode component
    dialogShowWifi(val) {
      if (val) { this.tempWifi = Object.assign({}, this.wifiSet) }
      this.wifiPanelSwitch = val
    },
    syncWifi() {
      this.wifiSet = Object.assign({}, this.tempWifi)
    },

    // Function for bulk edit component
    dialogShowGroup(val) {
      if (val) {
        this.tempWifi = { 'ssid': this.wifiSet.ssid, 'password': this.wifiSet.password }
        this.$refs.bulkEdit.updateDevice()
      } else {
        this.$refs.multipleTable.clearSelection()
        this.$refs.bulkEdit.clearConfig()
      }
      this.bulkPanelSwitch = val
    },

    // Send request for config edit panel and update table
    wifiToAp(val) {
      if (val) this.temp.wifi = Object.assign({}, this.wifiSet)
    },
    wifiDiff() {
      this.sameAsAP = false
    },
    handleUpdate(row) {
      this.temp = JSON.parse(JSON.stringify(row))
      this.sameAsAP = false
      this.editPanelSwitch = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          this.waitRequest = true
          var tempData = { 'device_config_json': { [this.temp.DeviceID]: {}}}
          var configAddress

          if (this.temp.ipAddress[this.interfaceName].ipMethod === 'manual') {
            const prefix = this.checkIpProperty(this.temp.ipAddress[this.interfaceName].ipArray)

            if (!prefix) {
              this.$message({
                message: 'Invalid value of IPv4 Address',
                type: 'warning'
              })
              this.waitRequest = false
              return
            }

            configAddress = `${this.interfaceName} manual ${this.temp.ipAddress[this.interfaceName].ipArray['IP Address'].join('.')} ${prefix}`

            if (!this.temp.ipAddress[this.interfaceName].ipArray['Gateway'].every((element) => element === '') && this.checkIpAddress(this.temp.ipAddress[this.interfaceName].ipArray, 'Gateway')) {
              configAddress = configAddress + ' ' + this.temp.ipAddress[this.interfaceName].ipArray['Gateway'].join('.')
            }
          } else { configAddress = `${this.interfaceName} auto` }

          tempData['device_config_json'][this.temp.DeviceID] = {
            'hostname': this.temp.Hostname,
            'wifi': `${this.temp.wifi.ssid} ${this.temp.wifi.password}`,
            'ip_address': configAddress
          }
          setConfigDiff(tempData).then(response => {
            if (this.responseVarify(response)) {
              const index = this.deviceList.findIndex(v => v.DeviceID === this.temp.DeviceID)
              this.deviceList.splice(index, 1, this.temp)
              this.editPanelSwitch = false
            }

            this.waitRequest = false
          })
        }
      })
    },

    // Function for task mode request
    handleTask(val, row) {
      if (confirm(`Click OK to switch task mode of ${row.Hostname} to "${val}"`)) {
        this.listLoading = true
        var tempData = { 'device_config_json': { [row.DeviceID]: { 'task_mode': val }}}
        setConfigDiff(tempData).then(() => {
          this.listLoading = false
          row['current_task'] = val
          this.$message({
            message: 'Task Launch Success',
            type: 'success'
          })
        })
      }
    },

    cidrToSubnet(bitCount) {
      var mask = []
      var n
      for (var i = 0; i < 4; i++) {
        n = Math.min(bitCount, 8)
        mask.push(String(256 - Math.pow(2, 8 - n)))
        bitCount -= n
      }
      return mask
    },
    deviceTypeFilter(name) {
      if (name === 'wifi') {
        return 'WiFi'
      } else if (name === 'ethernet') {
        return 'Ethernet'
      } else {
        return name
      }
    }
  }
}
</script>

<style lang="scss">
// Import Font Awesome 5 Free
$fa-css-prefix: 'el-icon-fa';
$fa-font-path: '~@fortawesome/fontawesome-free/webfonts';

@import '~@fortawesome/fontawesome-free/scss/fontawesome.scss';
@import '~@fortawesome/fontawesome-free/scss/regular.scss';
@import '~@fortawesome/fontawesome-free/scss/solid.scss';
@import '~@fortawesome/fontawesome-free/scss/brands.scss';

// Override Element UI's icon font
.fas {
  font-family: 'Font Awesome 5 Free' !important;
}

.fab {
  font-family: 'Font Awesome 5 Brands' !important;
}
</style>
