import axios from 'axios'
import router from '@/router'
import { API_TIMEOUT } from '@/utils/format'

const instance = axios.create({
  baseURL: '/',
  timeout: API_TIMEOUT,
})

instance.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

instance.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
    }
    return Promise.reject(err)
  }
)

export default instance
