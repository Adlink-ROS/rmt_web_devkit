import request from '@/utils/request'

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
