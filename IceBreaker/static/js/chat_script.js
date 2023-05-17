window.onload = function() {
    feather.replace()
}

document.addEventListener('DOMContentLoaded', function() {
    var connectionStatus = "online";
    const socket = io();
    console.log(socket.id);
    socket.emit('join_chat', {"Room": "<ROOM_ID>"}); 
    const chat = document.getElementById("chat-window");
    const all_buttons = document.querySelectorAll("button");

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
    function autoRegrow(element){
        element.style.height = "5px";
        element.style.height = (element.scrollHeight)+"px";
    }

    text_area = document.getElementById("message-textarea");
    submit_button = document.getElementById("send-button");

    submit_button.addEventListener("click", function(e){
        e.preventDefault();
        data = {"message": text_area.value, "time": "[DATA ZWRACANA PRZEZ SERVER]"};
        console.log(data);
        socket.emit("userMessage", data);

        chat.appendChild(createMessageField(data, "user"));
        text_area.value = "";
        
        autoRegrow(text_area);
    });

    function createMessageField(data, type){ //type: "user" or "partner"
        let messageField = document.createElement("div");
        let InfoField = document.createElement("div");
        let InfoFieldTime = document.createElement("p");
        let message = document.createElement("div");
        let messageContent = document.createElement("p");
        let profilePicture = document.createElement("div");
        let profilePictureImg = document.createElement("img");

        messageField.classList.add(type + "-message-field", "message-field");
        InfoField.classList.add("message-info");
        message.classList.add(type + "-message", "message");
        profilePicture.classList.add("user-chat-profile-picture", "chat-profile-picture");

        InfoFieldTime.innerHTML = data.time;
        messageContent.innerHTML = data.message;
        profilePictureImg.src = "{{url_for('static', filename='images/rickroll-roll.gif')}}";

        if(type === "user"){

            InfoField.appendChild(InfoFieldTime);
            messageField.appendChild(InfoField);

            message.appendChild(messageContent);
            messageField.appendChild(message);

            profilePicture.appendChild(profilePictureImg);
            messageField.appendChild(profilePicture);



        }else if(type === "partner"){

            let InfoFieldName = document.createElement("p");

            InfoFieldName.classList.add(type + "-name");
            InfoFieldName.innerHTML = data.author;

            InfoField.appendChild(InfoFieldName);
            InfoField.appendChild(InfoFieldTime);
            messageField.appendChild(InfoField);

            profilePicture.appendChild(profilePictureImg);
            messageField.appendChild(profilePicture);

            message.appendChild(messageContent);
            messageField.appendChild(message);
        }
        return messageField;
    };

    socket.on('partnerMessage', function(data) {
        console.log("Otrzymano wiadomość:");
    
        chat.appendChild(createMessageField(data, "partner"));
        
        console.log(data);
    });

});
/*
<main id="chat-window">
    <div class="user-message-field message-field">
        <div class="message-info">
            <p>22.04.2023 14:30</p>
        </div>
        <div class="user-message message">
            <p>Hello it is me! {{data.user_name}}</p>
        </div>
        <div class="user-chat-profile-picture chat-profile-picture">
            <img src="{{url_for('static', filename='images/rickroll-roll.gif')}}">
        </div>
    </div>

    <div class="partner-message-field message-field">
        <div class="message-info">
            <p class="partner-name">Piotr</p>
            <p>22.04.2023 14:30</p>
        </div>
        <div class="user-chat-profile-picture chat-profile-picture">
            <img src="{{url_for('static', filename='images/rickroll-roll.gif')}}">
        </div>
            <div class="partner-message message">
                <p>Test</p>
            </div>
        </div>
</main> 
*/