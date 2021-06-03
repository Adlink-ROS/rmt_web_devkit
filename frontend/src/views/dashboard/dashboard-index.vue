<template>
  <div class="app-container">

    <panel-group :total="total" :idle="idle" :running="running" :maintenance="maintenance" />

    <el-table
      ref="multipleTable"
      :key="tableKey"
      v-loading="listLoading"
      :default-sort="{prop: 'deviceID', order: 'ascending'}"
      :data="list"
      stripe
      fit
      highlight-current-row
      style="width: 100%;"
    >
      <el-table-column label="No." type="index" align="center" width="80" />
      <el-table-column label="Device ID" prop="deviceID" sortable :sort-orders="['ascending', 'descending']" width="110px" align="center">
        <template #default="{row}">
          <span>{{ row.deviceID }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Hostname" width="130px" align="center">
        <template #default="{row}">
          <span>{{ row.hostname }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Task Mode" width="130px" align="center">
        <template #default="{row}">
          <el-tag :type="statusTagMethod(row.task_mode)">{{ row.task_mode }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="WiFi Signal" width="130px" align="center">
        <template #default="{row}">
          <span>{{ row.wifi_rssi }} dBm</span>
        </template>
      </el-table-column>
      <el-table-column label="CPU Usage" width="160px" align="center">
        <template #default="{row}">
          <el-progress :percentage="row.cpu" :color="usageColorMethod" />
        </template>
      </el-table-column>
      <el-table-column label="RAM Usage" width="160px" align="center">
        <template #default="{row}">
          <el-progress :percentage="row.ram" :color="usageColorMethod" />
        </template>
      </el-table-column>
      <el-table-column label="Battery Level" width="160px" align="center">
        <template #default="{row}">
          <el-progress :percentage="99" :color="batteryColorMethod" />
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getList" />
  </div>
</template>

<script>
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import PanelGroup from './components/PanelGroup'
import io from 'socket.io-client'

export default {
  name: 'ComplexTable',
  components: { Pagination, PanelGroup },
  data() {
    return {
      tableKey: 0,
      percentage: 0,
      list: [],
      total: 0,
      idle: 0,
      running: 0,
      maintenance: 0,
      isIndeterminate: true,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 20
      },
      temp: {
        index: undefined
      },
      dialogStatus: ''
    }
  },
  created() {
    this.getList()
  },
  beforeDestroy() {
    this.socket.close()
  },
  methods: {
    getList() {
      const _this = this
      this.socket = io(process.env.VUE_APP_BASE_API + '/server', {
        transports: ['websocket']
      })
      this.socket.on('monitor_robot', function(data) {
        _this.list = data.items
        _this.total = data.total
        console.log(data.items)
        _this.countStatusNum(data.items)
        _this.listLoading = false
      })
    },
    countStatusNum(items) {
      var idle_cnt = 0
      var running_cnt = 0
      if (Object.keys(items).length === 0) {
        this.idle = 0
        this.running = 0
        return
      }
      items.forEach(item => {
        if (item.task_mode === 'Idle') {
          idle_cnt++
        } else {
          running_cnt++
        }
        this.idle = idle_cnt
        this.running = running_cnt
      })
    },
    usageColorMethod(percentage) {
      if (percentage < 30) {
        return '#67c23a'
      } else if (percentage < 70) {
        return '#6f7ad3'
      } else {
        return '#f56c6c'
      }
    },
    batteryColorMethod(percentage) {
      if (percentage < 50) {
        return '#f56c6c'
      } else if (percentage < 80) {
        return '#F9F900'
      } else {
        return '#67c23a'
      }
    },
    statusTagMethod(status) {
      if (status === 'Idle') {
        return 'info'
      } else if (status === 'Simulation') {
        return null
      } else {
        return 'success'
      }
    }
  }
}
</script>

