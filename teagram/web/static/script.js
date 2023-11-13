function showNotification(title, text) {
  let notificationContainer = document.getElementById("notification-container");
  
  let notification = document.createElement("div");
  notification.className = "notification";
  
  let notificationTitle = document.createElement("h3");
  notificationTitle.textContent = title;
  
  let notificationText = document.createElement("p");
  notificationText.textContent = text;
  
  notification.appendChild(notificationTitle);
  notification.appendChild(notificationText);
  
  notificationContainer.appendChild(notification);
  
  setTimeout(function() {
    notification.classList.add("show");
  }, 100);
  
  setTimeout(function() {
    notification.classList.remove("show");
    setTimeout(function() {
      notificationContainer.removeChild(notification);
    }, 300);
  }, 3000);
};

function showNotificationError(title, text) {
  let notificationContainer = document.getElementById("notification-container-err");
  
  let notification = document.createElement("div");
  notification.className = "notification-err";
  
  let notificationTitle = document.createElement("h3");
  notificationTitle.textContent = title;
  
  let notificationText = document.createElement("p");
  notificationText.textContent = text;
  
  notification.appendChild(notificationTitle);
  notification.appendChild(notificationText);
  
  notificationContainer.appendChild(notification);
  
  setTimeout(function() {
    notification.classList.add("show");
  }, 100);
  
  setTimeout(function() {
    notification.classList.remove("show");
    setTimeout(function() {
      notificationContainer.removeChild(notification);
    }, 300);
  }, 3000);
};

let tries = 0;
let __qr = true;
let _interval = null;

let _2fa = false;

function genqr(){
  let port = "";
  if (window.location.port){
    port = `:${window.location.port}`
  }

  fetch(`${window.location.href}qrcode${port}`, {method: "GET"})
  .then(
      (response) => {return response.text()}
  ).then(
      (data) => {
          let _qr = document.getElementById("qr_placeholder");
          let img = _qr.getElementsByTagName("canvas")[0]
        

          if (img){
            img.remove()
          }

          const qrCode = new QRCodeStyling({
            "width": 350,
            "height": 350,
            "data": data,
            "margin":5,
            "imageOptions":{
              "hideBackgroundDots":true,
              "imageSize":0.4,
              "margin":0
            },
            "dotsOptions":{
              "type":"extra-rounded",
              "color":"#000000",
              "gradient":null
            },
            "image": "https://avatars.githubusercontent.com/u/6113871"
          });

          qrCode.append(_qr)
          _qr.title = "";
      }
  )
}

function updating_qr(){
  tries += 1

  if (__qr) {
      let port = "";
      if (window.location.port){
        port = `:${window.location.port}`
      }

      fetch(`${window.location.href}checkqr${port}`, {method: "GET"})
      .then(
          (response) => {return response.text()}
      ).then(
          (data) => {
              if (data == 'password') {
                  __qr = false
                  _2fa = true
                  showNotification("2FA", 'Enter 2FA password')

                  document.getElementById(
                    "qr_placeholder"
                  ).remove()
              }                          
          }
      ).catch(
          (error) => {showNotificationError("ERROR", error); clearInterval(_interval)}
      )
      if (__qr && (tries == 10)){
          tries = 0

          genqr()
      }
  }else{
    clearInterval(_interval)
  }
}

async function post(endpoint, headers) {
  try {
      let port = "";
      if (window.location.port){
        port = `:${window.location.port}`
      }
      const response = await fetch(window.location.href + endpoint + port, {
      method: 'POST',
      headers: headers,
    });

    return await response.text();
  } catch (error) {
    showNotificationError("Error", error)
  }
}

document.getElementById("enter").onclick = async () => {
  if (!_2fa){
    const headers = new Headers()

    const _id = document.getElementById("api_id").value
    const _hash = document.getElementById("api_hash").value

    if (!_id || !_hash){
      showNotificationError("Error", "You didn't enter api_id or api_hash")
      return
    }

    headers.append('id', _id)
    headers.append('hash', _hash)

    try {
      const data = await post('tokens', headers);

      if (!data || data == null) {
        showNotification('Success', 'You are successfully logged, wait for inline bot!');
      } else if (data == 'qrcode') {
        showNotification('QRCode', 'Scan QRCode');
        if (!_interval){
          genqr();
          setInterval(updating_qr, 1000)
        }
      } else{
        console.log(data)
      }
    } catch (error) {
      console.error('Error:', error);
    }
  }else{
    if (__qr){
      showNotificationError("Error", "You didn't scan QRCode")
      return;
    }

    const headers = new Headers()
    const passwd = document.getElementById("password").value

    if (!passwd){
      showNotificationError("Error", "You didn't enter 2FA password")
      return
    }

    headers.append("2fa", passwd)

    try {
      const data = await post('twofa', headers)
      
      if (!data || data == null || data == "null") {
        showNotification('Success', 'You are successfully logged, wait for inline bot!');
      }else{
        console.log(data)
      }
    } catch(error) {
      console.log(data)
    }
  }  
}

const savedTheme = localStorage.getItem('theme');
if (savedTheme) {
  document.body.classList.add(savedTheme);
  let container = document.querySelector(".container")
  container.classList.toggle("dark-theme")
}

let themeToggle = document.getElementById("theme-toggle")
themeToggle.addEventListener("click", function() {
  document.body.classList.toggle("dark-theme")

  if (document.body.classList.contains("dark-theme")){
    localStorage.setItem('theme', 'dark-theme')
  }else{
    localStorage.setItem('theme', '')
  }

  let container = document.querySelector(".container")
  container.classList.toggle("dark-theme")
});
