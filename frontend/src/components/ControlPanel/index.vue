<template>
  <div>
    <el-dialog title="Control Panel" :visible.sync="dialogFormVisible" @close="closeDialog">
      <el-form ref="dataForm" :model="config" label-position="left" label-width="90px" style="width: 400px; margin-left:50px;">
        <el-form-item label="Robot ID">
          <span>{{ config.DeviceID }}</span>
        </el-form-item>
        <el-form-item label="Hostname">
          <span>{{ config.Hostname }}</span>
        </el-form-item>
        <el-row style="margin-top:20px">
          <el-switch
            v-model="locate_switch"
            active-text="ON"
            inactive-text="OFF"
            active-value="on"
            inactive-value="off"
          />
          <el-tooltip effect="light" content="Find ROScube with flashing LED">
            <el-button :loading="wait_request" type="primary" style="width: 120px; margin-left:50px" @click="handleLocate()">
              Locate
            </el-button>
          </el-tooltip>
        </el-row>
        <el-tooltip effect="dark" content="WARN!! Reboot ROScube">
          <el-button type="danger" style="width: 120px; margin-top:50px" @click="Reboot()">
            Reboot
          </el-button>
        </el-tooltip>
      </el-form>

      <div slot="footer" class="dialog-footer">
        <el-button @click="closeDialog">
          Done
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { set_config_diff } from '@/api/robots'

export default {
  props: {
    locate: {
      type: String,
      default: 'off'
    },
    dialogShow: {
      type: Boolean,
      default: false
    },
    config: {
      type: Object,
      default: () => {}
    }
  },
  data() {
    return {
      dialogFormVisible: this.dialogShow,
      wait_request: false,
      locate_switch: this.locate
    }
  },
  watch: {
    dialogShow(val) {
      this.dialogFormVisible = val
      this.locate_switch = this.locate
    }
  },
  methods: {
    closeDialog() {
      this.$emit('dialogShowChange', false)
    },
    Reboot() {
      this.$message({
        message: 'ROScube start reboot',
        type: 'warning'
      })
      this.locate_switch = this.locate
    },
    handleLocate() {
      var locate_json = { 'device_config_json': { [this.config.DeviceID]: { 'locate': this.locate_switch }}}
      this.wait_request = true
      set_config_diff(locate_json).then(() => {
        this.wait_request = false
        this.$message({
          message: 'ROSCube Locate Set',
          type: 'success'
        })
        this.$emit('syncData', this.locate_switch)
      })
    }
  }
}
</script>
