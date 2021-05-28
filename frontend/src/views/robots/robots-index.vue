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
        Group Edit
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
      <el-table-column type="selection" align="center" width="40" />
      <el-table-column label="Index" type="index" align="center" width="60" />
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

    <el-dialog :visible.sync="panel_on_edit">
      <el-tabs :value="default_tab">
        <el-tab-pane label="General" name="Config">General Settings
          <el-form ref="dataForm" :model="temp" label-position="left" label-width="90px" style="width: 400px; margin-left:50px; margin-top:20px">
            <el-form-item label="Hostname">
              <el-input v-model="temp.Hostname" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="WiFi" name="WiFi">RMT WiFi Client Configuration Settings
          <el-form ref="dataForm" :model="temp_wifi" label-position="left" label-width="90px" style="width: 400px; margin-left:50px; margin-top:20px">
            <el-form-item>
              <el-checkbox v-model="sameAsAP" border @change="wifi_to_ap">Same as AP Server</el-checkbox>
            </el-form-item>
            <el-form-item label="SSID">
              <el-input v-model="temp_wifi.ssid" maxlength="32" show-word-limit @input="wifi_diff" />
            </el-form-item>
            <el-form-item label="Password">
              <el-input v-model="temp_wifi.password" show-password minlength="8" maxlength="32" @input="wifi_diff" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      <div slot="footer" class="dialog-footer">
        <el-button v-waves @click="panel_on_edit = false">
          Cancel
        </el-button>
        <el-button v-waves :loading="wait_request" type="primary" @click="updateData()">
          Confirm
        </el-button>
      </div>
    </el-dialog>
    <control-component
      :dialog-show="panel_on_control"
      :config="temp"
      :locate="locate_list[temp.Index-1]"
      @dialogShowChange="dialogShowControl"
      @syncData="syncLocate"
    />
    <wifi-mode-component
      :dialog-show="panel_on_wifi"
      :wifi-set="temp_wifi"
      @dialogShowChange="dialogShowWifi"
      @syncData="syncWifi"
    />
    <bulk-edit-component
      :dialog-show="panel_on_group"
      :device-list="multipleSelection"
      :temp-wifi="temp_wifi"
      @dialogShowChange="dialogShowGroup"
      @syncData="syncGroupEdit"
    />
  </div>
</template>

<script>
import { fetchRobotList, set_config_diff, get_config_all, fetchWifi } from '@/api/robots'
import waves from '@/directive/waves' // waves directive
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import UploadExcelComponent from '@/components/UploadExcel/index_robot.vue'
import ControlComponent from '@/components/ControlPanel/index.vue'
import WifiModeComponent from '@/components/WiFiMode/index.vue'
import BulkEditComponent from '@/components/BulkEdit/index.vue'

export default {
  name: 'ComplexTable',
  components: { Pagination, UploadExcelComponent, ControlComponent, WifiModeComponent, BulkEditComponent },
  directives: { waves },
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
      wait_request: false,
      pageSetting: {
        page: 1,
        limit: 20
      },
      wifi_set: {
        ssid: '',
        password: '',
        band: '2.4 GHz',
        hotspot_enable: false
      },
      client_list: {},
      temp_wifi: {
        ssid: '',
        password: ''
      },
      temp: {
        index: undefined
      },
      locate_list: [],
      panel_on_group: false,
      panel_on_edit: false,
      panel_on_control: false,
      panel_on_wifi: false,
      default_tab: 'Config'
    }
  },
  created() {
    fetchWifi().then(response => {
      this.wifi_set = response.data
    }).then(this.getList())
  },
  methods: {
    getList() {
      this.listLoading = true
      var config = { 'config_list': ['wifi'] }
      fetchRobotList().then(response => {
        this.list = response.data.items
        this.total = response.data.total
        this.locate_list = Array(this.total).fill('off')
      }).then(() => get_config_all(config)).then(response => {
        Object.keys(response.data).forEach((element) => {
          var wifi_char = response.data[element].wifi.split(' ')
          if (wifi_char.length === 4) {
            this.client_list[element] = { 'ssid': wifi_char[1], 'password': wifi_char[3] }
          } else {
            this.$message({
              message: 'Agent WiFi Client Got Error',
              type: 'warning'
            })
          }
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
      this.panel_on_control = true
    },
    syncLocate(val) {
      this.locate_list[this.temp.Index - 1] = val
    },
    dialogShowControl(val) {
      this.panel_on_control = val
    },

    // Function for wifi ap mode component
    dialogShowWifi(val) {
      if (val) { this.temp_wifi = Object.assign({}, this.wifi_set) }
      this.panel_on_wifi = val
    },
    syncWifi() {
      this.wifi_set = Object.assign({}, this.temp_wifi)
    },

    // Function for bulk edit component
    dialogShowGroup(val) {
      if (val) { this.temp_wifi = { 'ssid': this.wifi_set.ssid, 'password': this.wifi_set.password } }
      this.panel_on_group = val
    },
    syncGroupEdit() {
      this.multipleSelection.forEach(element => {
        this.client_list[element.DeviceID] = Object.assign({}, this.temp_wifi)
      })
    },

    // Send request for config edit panel and update table
    wifi_to_ap(val) {
      if (val) {
        this.temp_wifi = Object.assign({}, this.wifi_set)
      } else {
        this.temp_wifi = Object.assign({}, this.client_list[this.temp.DeviceID])
      }
    },
    wifi_diff() {
      this.sameAsAP = false
    },
    handleUpdate(row) {
      this.temp = Object.assign({}, row) // copy obj
      this.temp_wifi = Object.assign({}, this.client_list[this.temp.DeviceID])
      this.sameAsAP = false
      this.panel_on_edit = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          this.wait_request = true
          var tempData = { 'device_config_json': { [this.temp.DeviceID]: {}}}
          var wifi_client_config = `${this.temp_wifi.ssid} ${this.temp_wifi.password}`
          tempData['device_config_json'][this.temp.DeviceID]['hostname'] = this.temp.Hostname
          tempData['device_config_json'][this.temp.DeviceID]['wifi'] = wifi_client_config
          set_config_diff(tempData).then(() => {
            const index = this.list.findIndex(v => v.DeviceID === this.temp.DeviceID)
            this.list.splice(index, 1, this.temp)
            this.client_list[this.temp.DeviceID] = Object.assign({}, this.temp_wifi)
            this.wait_request = false
            this.panel_on_edit = false
            this.$notify({
              title: 'Success',
              message: 'Update Successfully',
              type: 'success',
              duration: 2000
            })
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
        var list_index = this.list.findIndex(agent => agent.DeviceID === element['DeviceID'])
        this.list[list_index]['Hostname'] = element['Hostname']
      })
      set_config_diff(tempData).then(() => {
        this.listLoading = false
        this.$message({
          message: 'Configuration import success',
          type: 'success'
        })
      })
    }
  }
}
</script>

