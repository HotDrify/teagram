let output = document.querySelector('#output')
let _id = document.querySelector('#api_id')
let _hash = document.querySelector('#api_hash')
let phone = document.querySelector('#phone')
let code = document.querySelector('#phonecode')
let _2fa = document.querySelector('#_2fa')
let qr = false;
let __qr = false;   

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
            }else if(data == "choice"){
                alert("Scan qr")}

                let tries = 0;
                __qr = true;

                function genqr(){
                    fetch("http://127.0.0.1:8000/qrcode", {method: "GET"})
                    .then(
                        (response) => {return response.text()}
                    ).then(
                        (data) => {
                            let _qr = document.getElementById("_buttons");
                            let img = _qr.getElementsByTagName("img")[0]
                            if (img){
                                img.remove()
                            }                           
                            new QRCode(_qr, data.replace(/["']/g, ''));
                            _qr.title = ""                             
                        }
                    )
                }
                
                genqr()
                function updating_qr(){
                    tries += 1
                    if (__qr){
                        fetch("http://127.0.0.1:8000/checkqr", {method: "GET"})
                        .then(
                            (response) => {return response.text()}
                        ).then(
                            (data) => {
                                console.log(data)
                                if (data == '"password"'){
                                    __qr = false
                                    document.getElementById("_buttons").getElementsByTagName("img")[0].remove()
                                    alert("Enter 2fa")
                                }                          
                            }
                        ).catch(
                            (error) => {alert(error.text())}
                        )
                        if (__qr && (tries == 30)){
                            tries = 0

                            genqr()
                        }
                    }
                }
                setInterval(updating_qr, 1500)
            }
    )
}
document.querySelector('#entertwofa').onclick = () => {
    if (!_2fa.value){
        return alert('Enter 2fa password')
    }else{
        let headers = new Headers()
        headers.append('2fa', _2fa.value)     

        fetch(
            'http://127.0.0.1:8000/twofa',
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

                if (!data || data == null || data == 'null'){
                    alert('Logged in account, restarting')
                }else{
                    alert(data)
                }
            }
        )
    }
}