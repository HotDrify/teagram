let output = document.querySelector('#output')
let _id = document.querySelector('#api_id')
let _hash = document.querySelector('#api_hash')
let phone = document.querySelector('#phone')
let code = document.querySelector('#phonecode')
let _2fa = document.querySelector('#_2fa')

document.querySelector('#enterTokens').onclick = () => {
    let headers = new Headers()
    if (!_id.value){
        _id.value = ''
    }
    if (!_hash.value){
        _hash.value = ''
    }

    headers.append('id', _id.value)
    headers.append('hash', _hash.value)

    fetch(
        'http://127.0.0.1:8000/tokens',
        {
            method: 'POST',
            headers: headers
        }
    )
    .then(
        (response) => {return response.text()}
    ).then(
        (data) => {
            data = data.replace(/["']/g, '')
            
            if (data == 'Enter all api tokens'){
                return alert(data)
            }

            if (!data || data == null){
                alert('Logged in account, restarting')
            }else{
                alert(data)
            }
        }
    ).catch(
        (error) => {
            console.log('asjdla')
            alert(error)
        }
    )
}

document.querySelector('#enterPhone').onclick = () => {
    if (!phone.value){
        return alert('Enter phone number')
    }else{
        let headers = new Headers()
        headers.append('phone', phone.value)

        fetch(
            'http://127.0.0.1:8000/phone',
            {
                method: 'POST',
                headers: headers
            }
        )
        .then(
            (response) => {return response.text()}
        ).then(
            (data) => {alert(data.replace(/["']/g, ''))}
        )
    }
}
document.querySelector('#enterCode').onclick = () => {
    if (!code.value){
        return alert('Enter phone code')
    }else{
        let headers = new Headers()
        headers.append('code', code.value)
        if (_2fa.value){
            headers.append('2fa', _2fa.value)
        }

        fetch(
            'http://127.0.0.1:8000/code',
            {
                method: 'POST',
                headers: headers
            }
        )
        .then(
            (response) => {return response.text()}
        ).then(
            (data) => {
                if (!data || data == null || data == 'null'){
                    alert('Logged in account, restarting')
                }else{
                    alert(data.replace(/["']/g, ''))
                }
            }
        )
    }
}