export default {
  data() {
    return {}
  },
  methods: {
    responseVarify(response) {
      if (response.code !== 20000) {
        this.$notify({
          title: 'Error: Agent request failed',
          message: 'Request response status error',
          type: 'error',
          duration: 5000
        })
        return false
      }
      var result = true
      for (const [agentID, configList] of Object.entries(response['data'])) {
        for (const [configName, callbackValue] of Object.entries(configList)) {
          if (callbackValue === '-1') {
            this.$notify({
              title: 'Error: Agent request failed',
              dangerouslyUseHTMLString: true,
              message: `Agent:<b>${agentID}</b>\n<b>${configName}</b> Set Failed`,
              type: 'error',
              duration: 5000
            })
            result = false
          }
        }
      }
      if (result) {
        this.$notify({
          title: 'Success',
          message: 'Configuration Update Successfully',
          type: 'success',
          duration: 2000
        })
      }
      return result
    }
  }
}
