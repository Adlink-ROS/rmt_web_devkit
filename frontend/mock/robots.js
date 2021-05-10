const Mock = require('mockjs')

const List = []
const count = 100

const baseContent = '<p>I am testing data, I am testing data.</p><p><img src="https://wpimg.wallstcn.com/4c69009c-0fd4-4153-b112-6cb53d1cf943"></p>'

for (let i = 1; i <= count; i++) {
  List.push(Mock.mock({
    id: i,
    hostname: 'robot-'+i,
    'status|1': ['Active', 'Inactive'],
    'battery|1-100': 100,
    'cpu|1-100': 100,
    'memory|1-100': 100,
    'storage|1-100': 100,
    'timezone|1': ['Taipei', 'Tokyo', 'Moscow', 'London', 'New York', 'Los Angeles', 'Auckland'],
    content_short: 'mock data',
    content: baseContent
  }))
}

module.exports = [
  {
    url: '/robots/discovery',
    type: 'get',
    response: config => {
      const { type, title, page = 1, limit = 20, sort } = config.query

      let mockList = List.filter(item => {
        if (type && item.type !== type) return false
        if (title && item.title.indexOf(title) < 0) return false
        return true
      })

      if (sort === '-id') {
        mockList = mockList.reverse()
      }

      const pageList = mockList.filter((item, index) => index < limit * page && index >= limit * (page - 1))

      return {
        code: 20000,
        data: {
          total: mockList.length,
          items: pageList
        }
      }
    }
  },

  {
    url: '/robots/update',
    type: 'post',
    response: _ => {
      return {
        code: 20000,
        data: 'success'
      }
    }
  }
]

