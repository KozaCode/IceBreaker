window.onload = function() {
    feather.replace()
}

document.addEventListener('DOMContentLoaded', function() {
    let connectionStatus = "online";
    let displayUserProfilePicture = true;
    let displayPartnerProfilePicture = true;

    if(localStorage.getItem("display_user_profile_picture") === null){
        let state = true;
        localStorage.setItem("display_user_profile_picture", state)
        displayUserProfilePicture = state;
    }else{
        console.log("display_user_profile_picture:", localStorage.getItem("display_user_profile_picture"));
        console.log("display_user_profile_picture:", localStorage.getItem("display_user_profile_picture") === "true");
        displayUserProfilePicture = (localStorage.getItem("display_user_profile_picture") === "true");
    }

    if(localStorage.getItem("display_partner_profile_picture") === null){
        let state = true;
        localStorage.setItem("display_partner_profile_picture", state)
        displayPartnerProfilePicture = state;
    }else{
        console.log("display_partner_profile_picture:", localStorage.getItem("display_partner_profile_picture"));
        console.log("display_partner_profile_picture:", localStorage.getItem("display_partner_profile_picture") === "true");
        displayPartnerProfilePicture = (localStorage.getItem("display_partner_profile_picture") === "true");
    }

    const chat_header_status = document.getElementById("status-info");
    const text_area = document.getElementById("message-textarea");
    const submit_button = document.getElementById("send-button");
    const attachment_button = document.getElementById("attach-button");
    const info_button = document.getElementById("chat-header-info-button");
    const settings_button = document.getElementById("chat-header-settings-button");
    const close_button = document.getElementById("chat-header-close-button");
    const chat_header_name = document.getElementById("chat-header-name");
    const participants_dict = {};
    var infoContainer = null;
    var settingsContainer = null;
    var settingsApplyButton = null;

    const lightBox = document.getElementById("lightbox");
    lightBox.addEventListener("click", function(event){
        if(event.target === lightBox){
            lightBox.style.display = "none";
            for(const child of lightBox.children){
                child.style.display = "none";
            }
        }
    });


    if(!('indexedDB' in window)) {
        alert('This browser doesn\'t support IndexedDB!!!\nPlease use a different browser!\n\nOtherwise, your messages won\'t be saved!');
    }

    const socket = io();
    socket.emit('join_chat'); 
    console.log("Sending join_chat request...");
    const chat = document.getElementById("chat-window");
    var chatConfig = {};
    
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


    updateButtonStatus();

    function autoRegrow(area){
        area.style.height = "5px";
        area.style.height = (area.scrollHeight)+"px";
        if(area.value === ""){
            submit_button.disabled = true;
        }else{
            submit_button.disabled = false;
        }
    }

    function assembleMessage({"data": data, "messageDiv": messageDiv, "messageHeader": messageHeader, "messageTime": messageTime, "messageMainContainer": messageMainContainer, "messageContent": messageContent, "messageContentElement": messageContentElement, "messageAvatar": messageAvatar, "messageAvatarImage": messageAvatarImage, "sender": sender, "displayProfilePicture": displayProfilePicture}){
        if(sender === "user"){
            messageHeader.appendChild(messageTime);
            messageDiv.appendChild(messageHeader);

            messageContent.appendChild(messageContentElement);

            messageMainContainer.appendChild(messageContent);

            messageDiv.appendChild(messageMainContainer);

            if(displayProfilePicture){
                messageAvatar.appendChild(messageAvatarImage);
                messageDiv.appendChild(messageAvatar);
            }
        }else if(sender === "partner"){
            let messageAuthorElement = document.createElement("p");
            
            messageAuthorElement.classList.add(sender + "-name");
            messageAuthorElement.innerHTML = data.author;

            messageHeader.appendChild(messageAuthorElement);
            messageHeader.appendChild(messageTime);
            messageDiv.appendChild(messageHeader);

            if(displayProfilePicture){
                messageAvatar.appendChild(messageAvatarImage);
                messageDiv.appendChild(messageAvatar);
            }
            messageContent.appendChild(messageContentElement);

            messageMainContainer.appendChild(messageContent);

            messageDiv.appendChild(messageMainContainer);

        }
    }

    function createImageMessage(data, sender, messageContent, messageContentElement) {
        
        messageContent.classList.add(sender + "-message-image", "message-image", "max-width"); // user-message-image, partner-message-image, message-image

        let blob = new Blob([data.message]);
        let url = URL.createObjectURL(blob);

        messageContentElement = document.createElement("a");
        messageContentElement.href = url;
        messageContentElement.target = "_blank";
        messageContentElement.download = "image.png";

        messageContentElement.addEventListener("click", function(event){ //Prevent default download action
            event.preventDefault();
        });

        let image = document.createElement("img");
        image.src = url;

        image.addEventListener("click", function(){
            console.log("Image clicked!");

            const zoomImage = document.createElement("img");
            zoomImage.src = url;
            zoomImage.style.height = "80%";
            zoomImage.style.width = "auto";

            lightBox.appendChild(zoomImage);
            lightBox.style.display = "flex";

            console.log(lightBox);

            lightBox.addEventListener("click", function(event){
                if(event.target === lightBox){
                    zoomImage.remove();
                }
            })

            // zoomImage.addEventListener("click", function(event){ //Additional zoom on click
            //     let clickX = event.clientX;
            //     let clickY = event.clientY;
                
            //     let imageBoundingBox = zoomImage.getBoundingClientRect();
            //     console.log("Image bounding box:", imageBoundingBox);
            //     let imageClickX = clickX - imageBoundingBox.x;
            //     let imageClickY = clickY - imageBoundingBox.y;
            //     console.log("Clicked image at:", Math.round(imageClickX), Math.round(imageClickY));
 

            //     let imageRelativeCenterVertical = imageBoundingBox.x + imageBoundingBox.width/2;
            //     let imageRelativeCenterHorizontal = imageBoundingBox.y + imageBoundingBox.height/2;
            //     console.log("Clicked at:", clickX, clickY);
            //     console.log("Image center:", Math.round(imageRelativeCenterHorizontal), Math.round(imageRelativeCenterVertical));

            //     let differenceY = imageBoundingBox.height/2 - imageClickY;
            //     let differenceX = imageBoundingBox.width/2 - imageClickX;
            //     console.log("Difference:", Math.round(differenceX), Math.round(differenceY));

            //     zoomImage.style.transform = "scale(2)";
            //     // zoomImage.style.position = "fixed";
            //     zoomImage.style.transformOrigin = Math.round(-(differenceX)) + "px " + Math.round(-(differenceY)) + "px";
            //     // zoomImage.style.transition = "transform 0.5s ease";
            //     requestAnimationFrame(function(){
            //         imageBoundingBox = zoomImage.getBoundingClientRect();
            //         console.log("NEW Image bounding box:", imageBoundingBox);
            //     });
                
            // });

        });
        messageContentElement.appendChild(image);

        return messageContentElement;
    }

    function createVideoMessage(data, sender, contentType, messageContent, messageContentElement) {
        messageContent.classList.add(sender + "-message-video", "message-video"); // user-message-video, partner-message-video, message-video

        messageContentElement = document.createElement("video");
        messageContentElement.classList.add("video-js", "vjs-big-play-centered", "max-width");
        messageContentElement.id = "my-video";
        messageContentElement.className = "video-js";
        messageContentElement.controls = true;
        // messageContentElement.preload = "auto";
        // messageContentElement.muted = true;
        // messageContentElement.autoplay = true;
        // messageContentElement.loop = true;
        messageContentElement.dataset.setup = "{}";
        messageContentElement.dataset.message_id = data.message_id;


        let source = document.createElement("source");
        source.src = URL.createObjectURL(new Blob([data.message]));
        source.type = contentType;
        
        let noJsMessage = document.createElement("p");
        noJsMessage.className = "vjs-no-js";
        noJsMessage.innerHTML = 'Aby odtworzyć ten film, włącz JavaScript i rozważ aktualizację przeglądarki do <a href="https://videojs.com/html5-video-support/" target="_blank">obsługującej HTML5 video</a>';

        messageContentElement.appendChild(source);
        messageContentElement.appendChild(noJsMessage);

        return messageContentElement;
    }

    function createTextMessage(data, sender, messageContent, messageContentElement) {
        messageContent.classList.add(sender + "-message-text", "message-text", "max-width");
        messageContentElement = document.createElement("p");
        messageContentElement.innerHTML = data.message;
        return messageContentElement;
    }

    function setElementTime(messageTime, time){
        let date = new Date(time);
        messageTime.innerHTML = date.toLocaleDateString() + " " + date.toLocaleTimeString();
        messageTime.dataset.timestamp = time;
        messageTime.dataset.utc = time;
    }

    function createChatMessage(data, sender, contentType) {
        console.log("createChatMessage sender:", sender);
        console.log("createChatMessage contentType:", contentType);
        console.log("createChatMessage data:", data);
    
        let displayProfilePicture = ((sender === "user") && (displayUserProfilePicture === true)) || ((sender === "partner") && (displayPartnerProfilePicture === true))
    
        let messageDiv = document.createElement("div");
        let messageHeader = document.createElement("div");
        let messageTime = document.createElement("p");
        let messageMainContainer = document.createElement("div");
        let messageContent = document.createElement("div");
        let messageContentElement;
        let messageAvatar;
        let messageAvatarImage;
        if(displayProfilePicture){
            messageAvatar = document.createElement("div");
            messageAvatarImage = document.createElement("img");
        }
    
        messageDiv.classList.add(sender + "-message", "message");
        messageDiv.dataset.message_id = data.message_id;
    
        messageHeader.classList.add("message-header");
        
        if(displayProfilePicture){
            messageAvatar.classList.add("message-avatar");
        }
    
        // UTC to local time (YYYY-MM-DD HH:MM)
        setElementTime(messageTime, data.time);
        // let date = new Date(data.time);
        // messageTime.innerHTML = date.toLocaleDateString() + " " + date.toLocaleTimeString();
        // messageTime.dataset.timestamp = data.timestamp;
        // messageTime.dataset.utc = data.time;

        messageMainContainer.classList.add(sender + "-message-main-container", "message-main-container");

        if(contentType === "text"){ //Text message
            messageContentElement = createTextMessage(data, sender, messageContent, messageContentElement);

        } else if(contentType.includes("image")) { //Image container
            messageContentElement = createImageMessage(data, sender, messageContent, messageContentElement);

        } else if(contentType.includes("video")) { //Video player
            messageContentElement = createVideoMessage(data, sender, contentType, messageContent, messageContentElement);

        } else if(contentType.includes("audio")) {
            messageContentElement = document.createElement("audio");
            messageContentElement.src = URL.createObjectURL(new Blob([data.message]));
        }
    
        if(displayProfilePicture){
            messageAvatarImage.src = "static/images/rickroll-roll.gif";
        }
    
        assembleMessage({"data": data, "messageDiv": messageDiv, "messageHeader": messageHeader, "messageTime": messageTime, "messageMainContainer": messageMainContainer, "messageContent": messageContent, "messageContentElement": messageContentElement, "messageAvatar": messageAvatar, "messageAvatarImage": messageAvatarImage, "sender": sender, "displayProfilePicture": displayProfilePicture});
    
        chat.appendChild(messageDiv);

        if(contentType.includes("video")) {
            var player = videojs(messageContentElement);
            player.fluid(true);
            player.loop(true);
            player.muted(true);
            player.autoplay(true);
            player.preload(true);
            player.responsive(true);
        }
    }

    function reduceBreakLines(message){
        if (!message) return "";
        if (message.length < 2) return message;
        return message.replace(/\n+/g, "\n\n").replace(/\n+$/, "");
    }

    function countObjectSize(obj){
        var str = JSON.stringify(obj);
        var size = new Blob([str]).size;
        return size;
    }

    function sendMessage(message, message_type){ //SEND USER MESSAGE TO SERVER
        let data = {"message_id": crypto.randomUUID(),
            "message_type": message_type, //"text", "image/gif", "image/png", "image/jpeg", "video/mp4", "video/webm", "audio/mpeg", "audio/ogg", "audio/wav"
            "time": "",
            "timestamp": "",
            "author": chatConfig.user_name,
            "room": chatConfig.room
        };
        if(message_type === "text"){
            data.message = reduceBreakLines(message);
        }else{
            data.message = message;
            let sizeInBytes = message.byteLength;
            console.log("File size:", sizeInBytes, "bytes");
            console.log("File size:", Math.round(sizeInBytes/1024), "kB");
            console.log("File size:", Math.round(sizeInBytes/1024/1024), "MB");
        }
        try{
            createChatMessage(data, "user", data.message_type);
        }catch(err){
            console.log("Error while creating chat message:", err);
        }
        addMessageToDB(data.message_id, chatConfig.room, data.message_type, data.message, data.time, data.timestamp, chatConfig.user_name, chatConfig.user_id, "user");
        socket.emit("userMessage", data);
        text_area.value = "";
        autoRegrow(text_area);
    }

    socket.on('partnerMessage', function(data) { //RECEIVE PARTNER MESSAGE FROM SERVER
        console.log("Otrzymano wiadomość:", data);
        if(data.author_id === chatConfig.user_id){
            sender = "user";
        }else{
            sender = "partner";
        }
        if(data.room === chatConfig.room){
            createChatMessage(data, sender, data.message_type);
            console.log("Otrzymano wiadomość z TEGO SAMEGO pokoju co użytkownik!");
        }else{
            console.log("Otrzymano wiadomość z INNEGO pokoju niż użytkownik!");
        }

        addMessageToDB(data.message_id, data.room, data.message_type, data.message, data.time, data.timestamp, data.author, data.author_id, sender);
    });

    socket.on('updateMessageTime', function(data){
        console.log("Otrzymano aktualizację czasu wiadomości:", data);
        updateMessageTimeInDB(data).then((time) => {
            console.log("Czas wiadomości został zaktualizowany w bazie danych!");
            try {
                const message = document.querySelector("[data-message_id='" + data.message_id + "']");
                const messageInfo = message.querySelector(".message-header");
                const messageInfoTime = messageInfo.querySelector("p");
                setElementTime(messageInfoTime, time);
                // messageInfoTime.innerHTML = time;
            } catch (error) {
                console.log("Nie udało się zaktualizować czasu wiadomości na stronie!", error);
            }

        }).catch(err => {
            console.log(err);
        });
    });

    // When the submit button is clicked,
    // send the message in the text area to the server.
    submit_button.addEventListener("click", function(e){
        e.preventDefault();
        sendMessage(text_area.value, "text");
    });

    // when the user presses enter, send a message
    text_area.addEventListener("keypress", function(event){
        // if the user presses enter and shift, then just insert a new line
        if(event.key === "Enter" && !event.shiftKey){
            event.preventDefault();
            sendMessage(text_area.value, "text");
            text_area.value="";
        }
    });

    //updateButtonStatus checks the text_area value and enables or disables the submit button accordingly
    function updateButtonStatus(){
        submit_button.disabled = (text_area.value === "");
    }

    text_area.addEventListener("input", function(){
        try {
            autoRegrow(text_area);
            updateButtonStatus();
        }
        catch (e) {
            console.log("An error occurred: " + e);
        }
    });

    attachment_button.addEventListener("click", function(e){
        e.preventDefault();
        console.log("Attachment button clicked!");
        //upload file code
        let fileInput = document.createElement("input");
        fileInput.type = "file";
        fileInput.accept = "image/*, video/*, audio/*";
        fileInput.multiple = false;

        fileInput.addEventListener("change", function(e){
            let file = e.target.files[0];
            console.log("File: ", file);
            let reader = new FileReader();
            reader.onload = function(e){
                console.log("File loaded! File data: ", file.type, e.target.result);
                sendMessage(e.target.result, file.type);
            };
            reader.readAsArrayBuffer(file);
        });
        fileInput.click();
    });

    function createInfoContainer(){

        // HEADER
        infoContainer = document.createElement("div");
            infoContainer.id = "popup-container";

        const infoContainerHeader = document.createElement("div");
            infoContainerHeader.id = "popup-container-header";

        const infoContainerHeaderTitle = document.createElement("h1")
            infoContainerHeaderTitle.innerHTML = "Info about this chat";

        const infoContainerHeaderCloseButton = document.createElement("button");
            infoContainerHeaderCloseButton.id = "close-button";

        const infoContainerHeaderCloseButtonIcon = document.createElement("i");
            infoContainerHeaderCloseButtonIcon.setAttribute("data-feather", "x");

        infoContainerHeaderCloseButton.appendChild(infoContainerHeaderCloseButtonIcon);
        infoContainerHeader.appendChild(infoContainerHeaderTitle);
        infoContainerHeader.appendChild(infoContainerHeaderCloseButton);
        infoContainer.appendChild(infoContainerHeader);
        //HEADER

        //CONTENT
        const chatInfo = document.createElement("div");
        chatInfo.id = "chat-info";
        let listPopupItems = [];
        (() => {
            listPopupItems[0] = document.createElement("div");
            listPopupItems[0].classList.add("popup-item");

            
            const chatInfoItemTitle = document.createElement("h2");
                chatInfoItemTitle.innerHTML = "Chat name: ";
        
            const chatInfoItemContent = document.createElement("p");
                chatInfoItemContent.innerHTML = chatConfig.chat_name + " <span>" + chatConfig.room + "</span>";
                chatInfoItemContent.dataset.info = "room_name";
            
            listPopupItems[0].appendChild(chatInfoItemTitle);
            listPopupItems[0].appendChild(chatInfoItemContent);
            chatInfo.appendChild(listPopupItems[0]);
        })();

        (() => {
            listPopupItems[1] = document.createElement("div");
            listPopupItems[1].classList.add("popup-item");

            const chatInfoItemTitle = document.createElement("h2");
                chatInfoItemTitle.innerHTML = "User name" + (chatConfig.user_name === "" ? " (anonymous)" : "");
        
            const chatInfoItemContent = document.createElement("p");
                chatInfoItemContent.innerHTML = chatConfig.user_name + " <span>" + chatConfig.user_id + "</span>";
                chatInfoItemContent.dataset.info = "user_name";
            
            listPopupItems[1].appendChild(chatInfoItemTitle);
            listPopupItems[1].appendChild(chatInfoItemContent);
            chatInfo.appendChild(listPopupItems[1]);
        })();

        // (() => {
        //     listPopupItems[2] = document.createElement("div");
        //     listPopupItems[2].classList.add("popup-item");

        //     const chatInfoItemTitle = document.createElement("h2");
        //         chatInfoItemTitle.innerHTML = "User ID";

        //     const chatInfoItemContent = document.createElement("p");
        //         chatInfoItemContent.innerHTML = chatConfig.user_id;
        //         chatInfoItemContent.dataset.info = "user_id";
            
        //     listPopupItems[2].appendChild(chatInfoItemTitle);
        //     listPopupItems[2].appendChild(chatInfoItemContent);
        //     chatInfo.appendChild(listPopupItems[2]);
        // })();

        (() => {
            listPopupItems[3] = document.createElement("div");
            listPopupItems[3].classList.add("popup-item");
            
            const chatInfoItemTitle = document.createElement("h2");
                chatInfoItemTitle.innerHTML = "Created at";
            
            const chatInfoItemContent = document.createElement("p");
                setElementTime(chatInfoItemContent, chatConfig.created_at);
                // chatInfoItemContent.innerHTML = chatConfig.created_at;
            
            listPopupItems[3].appendChild(chatInfoItemTitle);
            listPopupItems[3].appendChild(chatInfoItemContent);
            chatInfo.appendChild(listPopupItems[3]);
        })();

        (() => {
            listPopupItems[4] = document.createElement("div");
            listPopupItems[4].classList.add("popup-item");

            const chatInfoItemTitle = document.createElement("h2");
                chatInfoItemTitle.innerHTML = "Participants:";
            
            listPopupItems[4].appendChild(chatInfoItemTitle);

            const listDivParticipants = document.createElement("div");
            listDivParticipants.id = "chat-participants";

            Object.entries(chatConfig.participants).forEach(([userId, userName]) => {
                const chatParticipant = document.createElement("div");
                chatParticipant.classList.add("chat-participant");
                chatParticipant.dataset.user_id = userId;

                const statusDot = document.createElement("div");
                statusDot.classList.add("status-dot", "dot-online");
                statusDot.dataset.user_id = userId;
                
                const chatParticipantName = document.createElement("p");
                chatParticipantName.innerHTML = userName + " <span>" + userId + "</span>";

                chatParticipant.appendChild(statusDot);
                chatParticipant.appendChild(chatParticipantName);
                listDivParticipants.appendChild(chatParticipant);
            });
            listPopupItems[4].appendChild(listDivParticipants);
            chatInfo.appendChild(listPopupItems[4]);
        })();
        
        infoContainer.appendChild(chatInfo);
    }

    function createSettingsContainer(){
    //HEADER
        settingsContainer = document.createElement("div");
            settingsContainer.id = "popup-container";

        const settingsContainerHeader = document.createElement("div");
            settingsContainerHeader.id = "popup-container-header";

        const settingsContainerHeaderTitle = document.createElement("h1")
            settingsContainerHeaderTitle.innerHTML = "Settings";

        const settingsContainerHeaderCloseButton = document.createElement("button");
            settingsContainerHeaderCloseButton.id = "close-button";

        const settingsContainerHeaderCloseButtonIcon = document.createElement("i");
            settingsContainerHeaderCloseButtonIcon.setAttribute("data-feather", "x");

        settingsContainerHeaderCloseButton.appendChild(settingsContainerHeaderCloseButtonIcon);
        settingsContainerHeader.appendChild(settingsContainerHeaderTitle);
        settingsContainerHeader.appendChild(settingsContainerHeaderCloseButton);
        settingsContainer.appendChild(settingsContainerHeader);
    //HEADER

    //CONTENT
        const settingsContent = document.createElement("div");
            settingsContent.id = "settings";

        const userSettingsSection = document.createElement("div");
            userSettingsSection.classList.add("settings-section");

        const userSettingsSectionTitle = document.createElement("h3");
            userSettingsSectionTitle.innerHTML = "User settings";

        const chatSettingsSection = document.createElement("div");
            chatSettingsSection.classList.add("settings-section");
        
        const chatSettingsSectionTitle = document.createElement("h3");
            chatSettingsSectionTitle.innerHTML = "Chat settings";

        chatSettingsSection.appendChild(chatSettingsSectionTitle);
        userSettingsSection.appendChild(userSettingsSectionTitle);

        settingsContent.appendChild(userSettingsSection);
        settingsContent.appendChild(chatSettingsSection);
    //CONTENT
    //USER SETTINGS userSettingsSection
        const userSettingsSectionContent = document.createElement("div");
            userSettingsSectionContent.id = "settings-section-content";
        let listUserSettingsItems = [];
        let dictChanges = {};
        (() => {
            listUserSettingsItems[0] = document.createElement("div");
            listUserSettingsItems[0].classList.add("popup-item");

            const userSettingTitle = document.createElement("h2");
                userSettingTitle.innerHTML = "Your name: ";
            
            const userSettingItem = document.createElement("input");
                userSettingItem.type = "text";
                userSettingItem.placeholder = "Your name";
                userSettingItem.classList.add("settings-input");
                userSettingItem.id = "user-name-input";
                userSettingItem.value = chatConfig.user_name;
                userSettingItem.dataset.info = "user_name";
                userSettingItem.dataset.default = chatConfig.user_name;
                userSettingItem.dataset.disabled = false;
                userSettingItem.dataset.local = false;
            
            listUserSettingsItems[0].appendChild(userSettingTitle);
            listUserSettingsItems[0].appendChild(userSettingItem);
            userSettingsSectionContent.appendChild(listUserSettingsItems[0]);
        })();
        (() => {
            listUserSettingsItems[1] = document.createElement("div");
            listUserSettingsItems[1].classList.add("popup-item");
            
            const userSettingTitle = document.createElement("h2");
                userSettingTitle.innerHTML = "Display your profile picture: ";
            
            const userSettingItem = document.createElement("input");
                userSettingItem.type = "checkbox";
                userSettingItem.classList.add("settings-input");
                userSettingItem.id = "display-user-profile-picture-input";
                userSettingItem.checked = displayUserProfilePicture;
                userSettingItem.value = displayUserProfilePicture;
                userSettingItem.dataset.info = "display_user_profile_picture";
                console.log("displayUserProfilePicture:", displayUserProfilePicture);
                userSettingItem.dataset.default = displayUserProfilePicture;
                userSettingItem.dataset.disabled = false;
                userSettingItem.dataset.local = true;

            listUserSettingsItems[1].appendChild(userSettingTitle);
            listUserSettingsItems[1].appendChild(userSettingItem);
            userSettingsSectionContent.appendChild(listUserSettingsItems[1]);
        })();
        (() => {
            listUserSettingsItems[2] = document.createElement("div");
            listUserSettingsItems[2].classList.add("popup-item");

            const userSettingTitle = document.createElement("h2");
                userSettingTitle.innerHTML = "Display partners' profile picture: ";
                
            const userSettingItem = document.createElement("input");
                userSettingItem.type = "checkbox";
                userSettingItem.classList.add("settings-input");
                userSettingItem.id = "display-partner-profile-picture-input";
                userSettingItem.checked = displayPartnerProfilePicture;
                userSettingItem.value = displayPartnerProfilePicture;
                userSettingItem.dataset.info = "display_partner_profile_picture";
                userSettingItem.dataset.default = displayPartnerProfilePicture;
                userSettingItem.dataset.disabled = false;
                userSettingItem.dataset.local = true;
            
            listUserSettingsItems[2].appendChild(userSettingTitle);
            listUserSettingsItems[2].appendChild(userSettingItem);
            userSettingsSectionContent.appendChild(listUserSettingsItems[2]);
        })();
        




        userSettingsSection.appendChild(userSettingsSectionContent);
    //CHAT SETTINGS chatSettingsSection
        const chatSettingsSectionContent = document.createElement("div");
            chatSettingsSectionContent.id = "settings-section-content";
        let listChatSettingsItems = [];
        (() => {
            listChatSettingsItems[0] = document.createElement("div");
            listChatSettingsItems[0].classList.add("popup-item");

            const chatSettingTitle = document.createElement("h2");
                chatSettingTitle.innerHTML = "Chat name: ";
            
            const chatSettingItem = document.createElement("input");
                chatSettingItem.type = "text";
                chatSettingItem.placeholder = "Chat name";
                chatSettingItem.classList.add("settings-input");
                chatSettingItem.id = "chat-name-input";
                chatSettingItem.value = chatConfig.chat_name;
                chatSettingItem.dataset.info = "chat_name";
                chatSettingItem.dataset.disabled = false;
                chatSettingItem.dataset.default = chatConfig.chat_name;
                chatSettingItem.dataset.local = false;

            listChatSettingsItems[0].appendChild(chatSettingTitle);
            listChatSettingsItems[0].appendChild(chatSettingItem);
            chatSettingsSectionContent.appendChild(listChatSettingsItems[0]);
        })();
        (() => {
            listChatSettingsItems[1] = document.createElement("div");
            listChatSettingsItems[1].classList.add("popup-item");

            const chatSettingTitle = document.createElement("h2");
                chatSettingTitle.innerHTML = "Let other to join this chat: ";
            
            const chatSettingItem = document.createElement("input");
                chatSettingItem.type = "checkbox";
                chatSettingItem.classList.add("settings-input");
                chatSettingItem.id = "allow-join-input";
                chatSettingItem.checked = chatConfig.allow_join;
                chatSettingItem.value = chatConfig.allow_join;
                chatSettingItem.dataset.info = "allow_join";
                chatSettingItem.dataset.local = false;
                chatSettingItem.dataset.disabled = false;
                chatSettingItem.dataset.default = chatConfig.allow_join;

            listChatSettingsItems[1].appendChild(chatSettingTitle);
            listChatSettingsItems[1].appendChild(chatSettingItem);
            chatSettingsSectionContent.appendChild(listChatSettingsItems[1]);
        })();
        (() => {
            listChatSettingsItems[2] = document.createElement("div");
            listChatSettingsItems[2].classList.add("popup-item");

            const chatSettingTitle = document.createElement("h2");
                chatSettingTitle.innerHTML = "Direct join key: ";
            
            const chatSettingItem = document.createElement("input");
                chatSettingItem.type = "text";
                chatSettingItem.placeholder = "Direct join key";
                chatSettingItem.classList.add("settings-input");
                chatSettingItem.id = "direct-join-key-input";
                chatSettingItem.value = chatConfig.direct_join_key;
                chatSettingItem.dataset.info = "direct_join_key";
                chatSettingItem.dataset.local = false;
                chatSettingItem.dataset.disabled = false;
                chatSettingItem.dataset.default = chatConfig.direct_join_key;

            listChatSettingsItems[2].appendChild(chatSettingTitle);
            listChatSettingsItems[2].appendChild(chatSettingItem);
            chatSettingsSectionContent.appendChild(listChatSettingsItems[2]);
        })();
        (() => {
            listChatSettingsItems[3] = document.createElement("div");
            listChatSettingsItems[3].classList.add("popup-item");

            const chatSettingTitle = document.createElement("h2");
                chatSettingTitle.innerHTML = "Chat password: ";
            
            const chatSettingItem = document.createElement("input");
                chatSettingItem.type = "text";
                chatSettingItem.placeholder = "[Empty = no password]"
                chatSettingItem.classList.add("settings-input");
                chatSettingItem.id = "chat-password-input";
                chatSettingItem.value = chatConfig.chat_password;
                chatSettingItem.dataset.info = "chat_password";
                chatSettingItem.dataset.local = false;
                chatSettingItem.dataset.disabled = false;
                chatSettingItem.dataset.default = chatConfig.chat_password;

            listChatSettingsItems[3].appendChild(chatSettingTitle);
            listChatSettingsItems[3].appendChild(chatSettingItem);
            chatSettingsSectionContent.appendChild(listChatSettingsItems[3]);
        })();

//Settings for server: user_name, chat_name, allow_join, direct_join_key, chat_password
        chatSettingsSection.appendChild(chatSettingsSectionContent);
     //Finish
        settingsContainer.appendChild(settingsContent);

        settingsApplyButton = document.createElement("button");
            settingsApplyButton.id = "settings-apply-button";
            settingsApplyButton.innerHTML = "Apply";
        
        settingsApplyButton.addEventListener("click", function(e){
            console.log("Settings apply button clicked!");
            var ignoreDefault = false;
            var ignoreDisabled = false;
            //read All changes from all sections and from all items
            for(const item of listUserSettingsItems.concat(listChatSettingsItems)){
                const input = item.querySelector("input");
                if(!ignoreDisabled && ('disabled' in input.dataset)){
                    if(input.dataset.disabled === "true"){
                        continue;
                    }
                }
                // if(input.type === "checkbox"){
                //     console.log(input.dataset.info, ":", input.checked, "default:", (input.dataset.default === "true"));
                // }
                console.log("DATA: ", input.dataset.info, ":", input.checked, "TYPE: ", input.type)
                if(input.type === "checkbox" && (ignoreDefault || input.checked !== (input.dataset.default === "true"))){
                    console.log(input.dataset.info, ":", input.checked, "default:", (input.dataset.default === "true"), "return value: ", input.checked);
                    dictChanges[input.dataset.info] = {
                        "value": input.checked,
                        "info": input.dataset.info,
                        "local": input.dataset.local
                    }
                }else if(ignoreDefault || input.value !== input.dataset.default){
                    dictChanges[input.dataset.info] = {
                        "value": input.value,
                        "info": input.dataset.info,
                        "local": input.dataset.local
                    }
                }
            }

            // for(const item of listChatSettingsItems){
            //     const input = item.querySelector("input");
            //     if(input.value !== input.dataset.default){
            //         const info = input.dataset.info;
            //         const value = input.value;

            //     }
            // }
            let needReload = false;
            let waitForReload = false;
            console.log("Changes: ");
            for(const [key, value] of Object.entries(dictChanges)){
                console.log(key, ":", value);
                if(value.local){
                    if(value.info === "display_user_profile_picture"){
                        // displayUserProfilePicture = value.value;
                        // console.log("DisplayUserProfilePicture value: ", value.value);
                        localStorage.setItem("display_user_profile_picture", value.value);
                    }else if(value.info === "display_partner_profile_picture"){
                        // displayPartnerProfilePicture = value.value;
                        // console.log("DisplayPartnerProfilePicture value: ", value.value);
                        localStorage.setItem("display_partner_profile_picture", value.value);
                    }
                }
                needReload = true;
            }
            const changesForServer = {};
            // const changesForServer = Object.entries(dictChanges).filter(([key,value]) => (value.local == "false"));
            for(let key in dictChanges){
                if(dictChanges[key].local === "false"){
                    changesForServer[key] = dictChanges[key].value;
                }
            }

            console.log("Changes for server: ", changesForServer);
            if(Object.keys(changesForServer).length > 0){
                console.log("SENDING CHANGES TO SERVER!")
                socket.emit("updateChatSettings", changesForServer);
                waitForReload = true;
            }

            if(needReload && !waitForReload){
                console.log("Reloading page...");
                location.reload();
            }
            //send changes to server
        }); 
        settingsContainer.appendChild(settingsApplyButton);

        console.log("First input value: ", listUserSettingsItems[0].querySelector("input").value);
    }
    
    info_button.addEventListener("click", function(e){

        if(!infoContainer){
            console.log("Creating info container...")
            createInfoContainer();
            lightBox.appendChild(infoContainer);
            const closeButton = infoContainer.querySelector("#close-button");
            closeButton.addEventListener("click", function(){
                lightBox.style.display = "none";
                infoContainer.style.display = "none";
            });
            feather.replace()
        }else{
            console.log("Info container already exists!");
            infoContainer.style.display = "flex";
        }
        lightBox.style.display = "flex";
    });

    settings_button.addEventListener("click", function(e){
        console.log("Settings button clicked!");
        if(!settingsContainer){
            console.log("Creating settings container...")
            createSettingsContainer();
            lightBox.appendChild(settingsContainer);
            const closeButton = settingsContainer.querySelector("#close-button");
            closeButton.addEventListener("click", function(){
                lightBox.style.display = "none";
                settingsContainer.style.display = "none";
            });
            feather.replace();
        }else{
            console.log("Settings container already exists!");
            settingsContainer.style.display = "flex";
        }
        lightBox.style.display = "flex";
    });

    function loadMessages(room_id){
        console.log("Loading messages for room:", room_id, "...")
        getMessagesFromDB(room_id).then(messages => {
            messages.sort(function(a, b){
                return a.timestamp - b.timestamp;
            });
            messages.forEach(message => {
                console.log("Loading message:", message);
                sender = message.sender
                if(message.author_id === chatConfig.user_id){
                    sender = "user";
                }
                createChatMessage({"message": message.content, "time": message.time, "author": message.author, "message_id": message.message_id}, message.sender, message.content_type);
            });
        }).catch(err => {
            console.log(err);
        });
    }

    socket.on('newParticipant', function(data) {
        console.log("New participant joined:", data);
        participants_dict[data.user_id] = {
            name: data.user_name,
            status: "online"
        };
    });

    socket.on('joined', function(data) {
        console.log("Joined!")
        chatConfig = data;
        console.log("Chat config:", chatConfig);
        const participantsEntries = Object.entries(chatConfig.participants);
        participantsEntries.forEach(([userId, userName]) => {
            participants_dict[userId] = { 
                name: userName,
                status: "online"
            };
        });
        if(participantsEntries.length === 2){
            let partnerName = "";
            participantsEntries.forEach(([userId, userName]) => {
                if(userId !== chatConfig.user_id){
                    partnerName = userName;
                }
            });
            chat_header_name.innerHTML = partnerName;
        }else{
            chat_header_name.innerHTML = chatConfig.chat_name;
        }
        dbReady.then(() => {
            loadMessages(chatConfig.room);
        });
    });

    socket.on('reload', function(data){
        console.log("Reload request received!");
        location.reload();
    });

    close_button.addEventListener("click", function(e){
        socket.emit("leave");
        window.location.href = "/";
    });
});