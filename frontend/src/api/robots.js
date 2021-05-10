import request from '@/utils/request'

export function fetchRobotList(query) {
  return request({
    url: '/robots/discovery',
    method: 'get',
    params: query
  })
}

export function set_config_diff(data) {
  return request({
    url: '/robots/set_diff_config_by_id',
    method: 'put',
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
