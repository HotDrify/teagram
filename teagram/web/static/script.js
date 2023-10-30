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
  fetch("http://localhost:8000/qrcode", {method: "GET"})
  .then(
      (response) => {return response.text()}
  ).then(
      (data) => {
          let _qr = document.getElementById("qr_placeholder");
          let img = _qr.getElementsByTagName("img")[0]

          if (img){
              img.remove()
          }

          new QRCode(
            _qr,
            {
              text: data.replace(/["']/g, ''),
              width: 350,
              height: 350
            }
          );
          _qr.title = "";
      }
  )
}

function updating_qr(){
  tries += 1

  if (__qr) {
      fetch("http://localhost:8000/checkqr", {method: "GET"})
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
      const response = await fetch('http://localhost:8000/' + endpoint, {
      method: 'POST',
      headers: headers,
    });

    const data = await response.text();
    return data.replace(/["']/g, '');
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
      showNotificationError("Unexpected error", error)
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
