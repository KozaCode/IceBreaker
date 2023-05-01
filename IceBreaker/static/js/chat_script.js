window.onload = function() {
    feather.replace()
}
var connectionStatus = "online";
function changeStatus(status){
    const chatHeaderStatus = document.getElementById("status-info");
    if(status === "online"){
        chatHeaderStatus.innerHTML = "Online<span id='status-dot'>";
        chatHeaderStatus.style.color = "#cccccc"
        document.getElementById("status-dot").style.backgroundColor = "#00ff00";
    } else {
        chatHeaderStatus.innerHTML = "Offline<span id='status-dot'>"
        chatHeaderStatus.style.color = "#737373"
        document.getElementById("status-dot").style.backgroundColor = "#770000";
    }
}
function toggleStatus(){
    if(connectionStatus === "online"){
      connectionStatus = "offline";
    } else {
      connectionStatus = "online";
    }
    changeStatus(connectionStatus);
}
setInterval(toggleStatus, 1000);

function auto_regrow(element){
    element.style.height = "5px";
    element.style.height = (element.scrollHeight)+"px";
}
