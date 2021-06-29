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
            v-model="locateSwitch"
            active-text="ON"
            inactive-text="OFF"
            active-value="on"
            inactive-value="off"
          />
          <el-tooltip effect="light" content="Find ROScube with flashing LED">
            <el-button :loading="waitRequest" type="primary" style="width: 120px; margin-left:50px" @click="handleLocate()">
              Locate
            </el-button>
          </el-tooltip>
        </el-row>
        <el-row style="margin-top:20px">
          <span> This function is only workable if the device has LED.</span>
        </el-row>
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
import { setConfigDiff } from '@/api/robots'

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
      waitRequest: false,
      locateSwitch: this.locate
    }
  },
  watch: {
    dialogShow(val) {
      this.dialogFormVisible = val
      this.locateSwitch = this.locate
    }
  },
  methods: {
    closeDialog() {
      this.$emit('dialogShowChange', false)
    },
    handleLocate() {
      var tempData = { 'device_config_json': { [this.config.DeviceID]: { 'locate': this.locateSwitch }}}
      this.waitRequest = true
      setConfigDiff(tempData).then(() => {
        this.waitRequest = false
        this.$message({
          message: 'ROSCube Locate Set',
          type: 'success'
        })
        this.$emit('syncData', this.locateSwitch)
      })
    }
  }
}
</script>
