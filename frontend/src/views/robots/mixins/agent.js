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
    },
    checkIpProperty(agentIp) {
      if (!this.checkIpAddress(agentIp, 'IP Address') || !this.checkIpAddress(agentIp, 'Subnet Mask')) {
        return false
      } else if (!agentIp['Gateway'].every((element) => element === '') && !this.checkIpAddress(agentIp, 'Gateway')) {
        return false
      }
      var bitcode = agentIp['Subnet Mask'].reduce((total, current) => {
        return total + Number(current).toString(2).padStart(8, '0')
      }, '')

      if (bitcode.split('01').length >= 2) {
        return false
      }
      const prefix = bitcode.split('1').length - 1

      return prefix
    },
    checkIpAddress(agentIp, ipArray) {
      var ipCheck = agentIp[ipArray].join('.')
      return (/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(ipCheck))
    }
  }
}
