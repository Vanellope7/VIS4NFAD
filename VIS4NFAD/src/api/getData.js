import service from '../utils/$axios.js'

export function getData(){
    return service({
        method:'get',
        url:'/getData',
    })
}