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
}

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
}
  
let modalContainer = document.getElementById("modal-container");
let showModalButton = document.getElementById("show-modal");

showModalButton.addEventListener("click", function() {
  let modal = document.createElement("div");
  modal.className = "modal";
  
  let modalOverlay = document.createElement("div");
  modalOverlay.className = "modal-overlay";
  
  let modalContent = document.createElement("div");
  modalContent.className = "modal-content";
  
  let close = document.createElement("span");
  close.className = "close";
  close.innerHTML = "&times;";
  
  let modalTitle = document.createElement("h3");
  modalTitle.className = "modal-title";
  modalTitle.textContent = "Заголовок окна";
  
  let modalText = document.createElement("p");
  modalText.className = "modal-text";
  modalText.textContent = "Текст окна";
  
  let modalButton = document.createElement("button");
  modalButton.id = "modal-button";
  modalButton.textContent = "Закрыть";
  
  modalContent.appendChild(close);
  modalContent.appendChild(modalTitle);
  modalContent.appendChild(modalText);
  modalContent.appendChild(modalButton);
  
  modal.appendChild(modalOverlay);
  modal.appendChild(modalContent);
  
  modalContainer.appendChild(modal);
  
  close.addEventListener("click", function() {
    modalContainer.removeChild(modal);
  });
  
  modalButton.addEventListener("click", function() {
    modalContainer.removeChild(modal);
  });
  
  modalOverlay.addEventListener("click", function() {
    modalContainer.removeChild(modal);
  });
  
  document.addEventListener("keydown", function(event) {
    if (event.key === "Escape") {
      modalContainer.removeChild(modal);
    }
  });
})

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

          console.log("GENERATED QRCODE, TRY: ", tries)
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
              if (data == '"password"') {
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
    throw error;
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

      if (!data || data === null) {
        showNotification('Success', 'You are successfully logged, wait for inline bot!');
      } else if (data === 'qrcode') {
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

let themeToggle = document.getElementById("theme-toggle");
themeToggle.addEventListener("click", function() {
  document.body.classList.toggle("dark-theme");
  let container = document.querySelector(".container");
  container.classList.toggle("dark-theme");
});
