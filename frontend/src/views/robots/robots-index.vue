<template>
  <div class="app-container">

    <div class="filter-container">
      <el-button v-waves class="filter-item" type="primary" icon="el-icon-search" @click="getList()">
        Search
      </el-button>
      <el-button v-waves class="filter-item" type="primary" icon="el-icon-refresh" style="width: 110px" @click="list=[]">
        Clear
      </el-button>
      <el-button v-waves class="filter-item" type="primary" icon="el-icon-download" @click="handleDownload()">
        Export
      </el-button>
      <upload-excel-component class="filter-item" style="margin-left:9px; margin-right:9px;" :on-success="handleSuccess" :before-upload="beforeUpload" />
      <el-button v-waves class="filter-item" type="primary" icon="el-icon-location-outline" @click="dialogShowWifi(true)">
        WiFi mode
      </el-button>
      <el-button v-show="multipleSelection.length" v-waves class="filter-item" type="primary" icon="el-icon-set-up" @click="dialogShowGroup(true)">
        Bulk Edit
      </el-button>
    </div>

    <el-table
      ref="multipleTable"
      :key="tableKey"
      v-loading="listLoading"
      :default-sort="{prop: 'DeviceID', order: 'ascending'}"
      :data="list"
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
      <!-- <el-table-column label="RMT version" width="110px" align="center">
        <template #default="{row}">
          <span>{{ row.RMT_VERSION }}</span>
        </template>
      </el-table-column> -->
      <el-table-column label="Actions" align="center" width="150" class-name="small-padding fixed-width">
        <template #default="{row}">
          <el-button v-waves type="info" size="mini" @click="handleUpdate(row)">
            Edit
          </el-button>
          <el-button v-waves type="primary" size="mini" @click="handlecontrol(row)">
            Control
          </el-button>
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

    <el-dialog title="Export Excel" :visible.sync="downloadLoading">
      <el-form ref="dataForm" label-position="left" label-width="80px" style="width: 400px; margin-left:50px;">
        <el-form-item label="File name">
          <el-input v-model="filename" />
        </el-form-item>
      </el-form>
      <template>
        <el-checkbox v-model="checkAll" :indeterminate="isIndeterminate" @change="handleCheckAllChange">Check all</el-checkbox>
        <div style="margin: 15px 0;" />
        <el-checkbox-group v-model="checkedParams" @change="handleCheckedParamChange">
          <el-checkbox v-for="param in ParamOption" :key="param" :label="param">{{ param }}</el-checkbox>
        </el-checkbox-group>
      </template>
      <div slot="footer" class="dialog-footer">
        <el-button v-waves @click="downloadLoading = false">
          Cancel
        </el-button>
        <el-button v-waves type="primary" @click="handleConfirm">
          Confirm
        </el-button>
      </div>
    </el-dialog>

    <el-dialog :visible.sync="editPanelSwitch">
      <el-tabs :value="defaultTabName">
        <el-tab-pane label="General" name="Config">General Settings
          <el-form ref="dataForm" :model="temp" label-position="left" label-width="90px" style="width: 400px; margin-left:50px; margin-top:20px">
            <el-form-item label="Hostname">
              <el-input v-model="temp.Hostname" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="WiFi" name="WiFi">RMT WiFi Client Configuration Settings
          <el-form ref="dataForm" :model="tempWifi" label-position="left" label-width="90px" style="width: 400px; margin-left:50px; margin-top:20px">
            <el-form-item>
              <el-checkbox v-model="sameAsAP" border @change="wifiToAp">Same as AP Server</el-checkbox>
            </el-form-item>
            <el-form-item label="SSID">
              <el-input v-model="tempWifi.ssid" maxlength="32" show-word-limit @input="wifiDiff" />
            </el-form-item>
            <el-form-item label="Password">
              <el-input v-model="tempWifi.password" show-password minlength="8" maxlength="32" @input="wifiDiff" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="IPv4" name="IPv4">IPv4 Address
          <el-form label-position="left" label-width="90px" style="width: 90%; margin-left:50px; margin-top:20px">
            <el-row>
              <el-radio v-model="tempWifi.ipMethod" label="auto">Automatic (DHCP)</el-radio>
              <el-radio v-model="tempWifi.ipMethod" label="manual">Manual</el-radio>
            </el-row>
            <div v-for="(ipArray, key) in tempWifi.ipArray" :key="key">
              <el-row class="ip-header">
                <el-col :span="5"><span>{{ key }}</span></el-col>
              </el-row>
              <el-row>
                <el-input
                  v-for="(segment, index) in ipArray"
                  :key="index"
                  v-model="ipArray[index]"
                  maxlength="3"
                  :disabled="tempWifi.ipMethod=='auto'"
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
          Confirm
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
      :dialog-show="bulkPanelSwitch"
      :device-list="multipleSelection"
      :temp-wifi="tempWifi"
      @dialogShowChange="dialogShowGroup"
      @syncData="syncGroupEdit"
    />
  </div>
</template>

<script>
import { fetchRobotList, setConfigDiff, getConfigAll, fetchWifi } from '@/api/robots'
import agentItem from './mixins/agent'
import waves from '@/directive/waves' // waves directive
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import UploadExcelComponent from './components/UploadExcel'
import ControlComponent from './components/ControlPanel'
import WifiModeComponent from './components/WiFiMode'
import BulkEditComponent from './components/BulkEdit'

export default {
  name: 'ComplexTable',
  components: { Pagination, UploadExcelComponent, ControlComponent, WifiModeComponent, BulkEditComponent },
  directives: { waves },
  mixins: [agentItem],
  data() {
    return {
      tableKey: 0,
      list: [],
      total: 0,
      multipleSelection: [],
      downloadLoading: false,
      checkAll: false,
      sameAsAP: false,
      filename: '',
      ParamOption: [],
      checkedParams: [],
      isIndeterminate: true,
      listLoading: true,
      waitRequest: false,
      pageSetting: {
        page: 1,
        limit: 20
      },
      wifiSet: {},
      wifiClientList: {},
      tempWifi: {},
      temp: {},
      locateList: [],
      bulkPanelSwitch: false,
      editPanelSwitch: false,
      controlPanelSwitch: false,
      wifiPanelSwitch: false,
      defaultTabName: 'Config'
    }
  },
  created() {
    fetchWifi().then(response => {
      this.wifiSet = response.data
    }).then(this.getList())
  },
  methods: {
    getList() {
      this.listLoading = true
      var config = { 'config_list': ['wifi', 'task_list', 'task_mode', 'ip_address'] }
      fetchRobotList().then(response => {
        this.list = response.data.items
        this.total = response.data.total
        this.locateList = Array(this.total).fill('off')
      }).then(() => getConfigAll(config)).then(response => {
        Object.keys(response.data).forEach((element) => {
          var splitWifiString = response.data[element].wifi.split(' ')
          var splitIpString = response.data[element]['ip_address'].split(' ')
          this.wifiClientList[element] = { 'ssid': splitWifiString[1], 'password': splitWifiString[3] }
          this.wifiClientList[element]['ipMethod'] = splitIpString[0]
          if (splitIpString.length > 1) {
            this.wifiClientList[element]['ipArray'] = {
              'IP Address': splitIpString[1].split('.'),
              'Subnet Mask': this.cidrToSubnet(splitIpString[2])
            }
            if (splitIpString.length > 3) {
              this.wifiClientList[element]['ipArray']['Gateway'] = splitIpString[3].split('.')
            } else {
              this.wifiClientList[element]['ipArray']['Gateway'] = Array(4).fill('')
            }
          } else {
            this.wifiClientList[element]['ipArray'] = {
              'IP Address': Array(4).fill(''),
              'Subnet Mask': Array(4).fill(''),
              'Gateway': Array(4).fill('')
            }
          }
          var splitTaskString = response.data[element].task_list.split(' ')
          var listIndex = this.list.findIndex(agent => agent.DeviceID === element)
          this.list[listIndex]['task_list'] = splitTaskString
          this.list[listIndex]['current_task'] = response.data[element].task_mode
        })
        this.listLoading = false
      })
    },

    // Handle agents selection in table
    handleSelectionChange(val) {
      this.multipleSelection = val
    },

    // Handle parameter checkbox
    handleCheckAllChange(val) {
      this.checkedParams = val ? this.ParamOption : []
      this.isIndeterminate = false
    },
    handleCheckedParamChange(value) {
      const checkedCount = value.length
      this.checkAll = checkedCount === this.ParamOption.length
      this.isIndeterminate = checkedCount > 0 && checkedCount < this.ParamOption.length
    },

    // Function for downloading configuration as excel file
    handleDownload() {
      if (this.multipleSelection.length) {
        this.ParamOption = Object.keys(this.list[0])
        this.downloadLoading = true
      } else {
        this.$message({
          message: 'Please select at least one item',
          type: 'warning'
        })
      }
    },
    formatJson(filterVal, jsonData) {
      return jsonData.map(v => filterVal.map(j => v[j]))
    },
    handleConfirm() {
      import('@/vendor/Export2Excel').then(excel => {
        const filterVal = this.checkedParams
        const tHeader = filterVal
        const list = this.multipleSelection
        const data = this.formatJson(filterVal, list)
        excel.export_json_to_excel({
          header: tHeader,
          data,
          filename: this.filename
        })
        this.$refs.multipleTable.clearSelection()
        this.downloadLoading = false
      })
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
      } else {
        this.$refs.multipleTable.clearSelection()
      }
      this.bulkPanelSwitch = val
    },
    syncGroupEdit(configName) {
      if (configName === 'wifi') {
        this.multipleSelection.forEach(element => {
          this.wifiClientList[element.DeviceID] = Object.assign(this.wifiClientList[element.DeviceID],
            (({ ssid, password }) => ({ ssid, password }))(this.tempWifi))
        })
      } else if (configName === 'IPv4') {
        this.multipleSelection.forEach((element) => {
          this.wifiClientList[element.DeviceID] = Object.assign(this.wifiClientList[element.DeviceID],
            (({ ipMethod, ipArray }) => ({ ipMethod, ipArray }))(this.tempWifi))
        })
      } else if (configName === 'IPv4Seq') {
        this.multipleSelection.forEach((element, index) => {
          var templateIp = JSON.parse(JSON.stringify(this.tempWifi))
          this.wifiClientList[element.DeviceID] = Object.assign(this.wifiClientList[element.DeviceID],
            (({ ipMethod, ipArray }) => ({ ipMethod, ipArray }))(templateIp))
          this.wifiClientList[element.DeviceID].ipArray['IP Address'][3] = String(index + +this.wifiClientList[element.DeviceID].ipArray['IP Address'][3])
        })
      }
    },

    // Send request for config edit panel and update table
    wifiToAp(val) {
      if (val) {
        this.tempWifi = Object.assign({}, this.wifiSet)
      } else {
        this.tempWifi = Object.assign({}, this.wifiClientList[this.temp.DeviceID])
      }
    },
    wifiDiff() {
      this.sameAsAP = false
    },
    handleUpdate(row) {
      this.temp = Object.assign({}, row) // copy obj
      this.tempWifi = JSON.parse(JSON.stringify(this.wifiClientList[this.temp.DeviceID]))
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

          if (this.tempWifi.ipMethod === 'manual') {
            const prefix = this.checkIpProperty(this.tempWifi.ipArray)

            if (!prefix) {
              this.$message({
                message: 'Invalid value of IPv4 Address',
                type: 'warning'
              })
              this.waitRequest = false
              return
            }

            configAddress = `manual ${this.tempWifi.ipArray['IP Address'].join('.')} ${prefix}`

            if (!this.tempWifi.ipArray['Gateway'].every((element) => element === '') && this.checkIpAddress(this.tempWifi.ipArray, 'Gateway')) {
              configAddress = configAddress + ' ' + this.tempWifi.ipArray['Gateway'].join('.')
            }
          } else { configAddress = 'auto' }

          tempData['device_config_json'][this.temp.DeviceID] = {
            'hostname': this.temp.Hostname,
            'wifi': `${this.tempWifi.ssid} ${this.tempWifi.password}`,
            'ip_address': configAddress
          }
          setConfigDiff(tempData).then(response => {
            if (this.responseVarify(response)) {
              const index = this.list.findIndex(v => v.DeviceID === this.temp.DeviceID)
              this.list.splice(index, 1, this.temp)
              this.wifiClientList[this.temp.DeviceID] = Object.assign(this.wifiClientList[this.temp.DeviceID], this.tempWifi)
              this.editPanelSwitch = false
            }

            this.waitRequest = false
          })
        }
      })
    },

    // File check for import excel and update table
    beforeUpload(file) {
      const isLt1M = file.size / 1024 / 1024 < 1
      if (isLt1M) {
        return true
      }
      this.$message({
        message: 'Please do not upload files larger than 1m in size.',
        type: 'warning'
      })
      return false
    },
    handleSuccess({ results, header }) {
      this.listLoading = true
      var tempData = { 'device_config_json': {}}

      results.forEach((element) => {
        tempData['device_config_json'] = { [element['DeviceID']]: { 'hostname': element['Hostname'] }}
        var listIndex = this.list.findIndex(agent => agent.DeviceID === element['DeviceID'])
        this.list[listIndex]['Hostname'] = element['Hostname']
      })
      setConfigDiff(tempData).then(() => {
        this.listLoading = false
        this.$message({
          message: 'Configuration import success',
          type: 'success'
        })
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
    }
  }
}
</script>
