// api.js
import axios from 'axios'
// import { Message } from 'element-ui'

const service = axios.create({
    baseURL: process.env.VUE_APP_BASE_API,
    timeout: 5000 // 请求超时时间
})

// 请求拦截器
service.interceptors.request.use(
    config => {
        // 在这里可以统一设置请求头等信息
        return config
    },
    error => {
        // 请求错误时的处理
        return Promise.reject(error)
    }
)

// 响应拦截器
service.interceptors.response.use(
    response => {
        const res = response.data

        // 在这里可以统一处理接口返回的错误码等信息
        if (res.code !== 0) {
            // Message({
            //     message: res.message || 'Error',
            //     type: 'error',
            //     duration: 5 * 1000
            // })

            return Promise.reject(new Error(res.message || 'Error'))
        } else {
            return res
        }
    },
    error => {
        // 响应错误时的处理
        return Promise.reject(error)
    }
)

export default service