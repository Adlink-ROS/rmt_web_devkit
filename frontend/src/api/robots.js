import request from '@/utils/request'
import { Notification } from 'element-ui'

export function fetchRobotList() {
  return request({
    url: '/robots/discovery',
    method: 'get'
  })
}

export function setConfigDiff(data) {
  return request({
    url: '/robots/set_diff_config_by_id',
    method: 'put',
    data
  })
}

export function setConfigSequential(data) {
  return request({
    url: '/robots/set_sequential_config_by_id',
    method: 'put',
    data
  })
}

export function setConfigSame(data) {
  return request({
    url: '/robots/set_same_config_by_id',
    method: 'put',
    data
  })
}

export function getConfigAll(data) {
  return request({
    url: '/robots/get_config_for_all',
    method: 'post',
    data
  })
}

export function updateWifi(data) {
  return request({
    url: '/robots/set_wifi_hotspot',
    method: 'post',
    data
  })
}

export function fetchWifi() {
  return request({
    url: '/robots/get_wifi_hotspot',
    method: 'get'
  })
}

export function responseVarify(response) {
  for (const [agentID, configList] of Object.entries(response['data'])) {
    for (const [configName, callbackValue] of Object.entries(configList)) {
      if (callbackValue === '0') {
        Notification({
          title: 'Success',
          message: 'Configuration Update Successfully',
          type: 'success',
          duration: 2000
        })
      } else {
        Notification({
          title: 'Error: Agent request failed',
          dangerouslyUseHTMLString: true,
          message: `Agent:<b>${agentID}</b>\n<b>${configName}</b> Set Failed`,
          type: 'error',
          duration: 5000
        })
      }
    }
  }
}
