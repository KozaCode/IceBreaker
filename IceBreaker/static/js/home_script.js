document.addEventListener('DOMContentLoaded', function() {
    const socket = io();
    
    user_name = data.user_name;
    already_logged_in = user_name != '';

    if(already_logged_in){
        document.getElementById('welcome-message').classList.remove('hidden');
    }
    //connection test
    socket.on('connect', function() {
        console.log('connected');
        console.log('user_name: ', user_name);
        console.log('already_logged_in: ', already_logged_in);
    });
    socket.on('roomCreated', function(data) {
        console.log('roomCreated');
        window.location.href = '/chat';
    });
    socket.on('roomJoined', function(data) {
        console.log('roomJoined');
        window.location.href = '/chat';
    });

    const random_pairing_button = document.getElementById('random-pairing');
    const connect_direct_button = document.getElementById('connect-direct');
    const create_room_button = document.getElementById('create-room');
    const your_rooms_button = document.getElementById('your-rooms');
    const settings_button = document.getElementById('settings');
    const lightboxes = document.querySelectorAll('.lightbox');

    lightboxes.forEach(function(element) {
        element.addEventListener('click', function(event) {
            if (event.target === element){
                element.classList.remove('active');
            }
        });
    });

    const rooms_list_lightbox = document.getElementById('lightbox-rooms-list')
    const rooms_buttons = rooms_list_lightbox.querySelectorAll('.room')

    rooms_buttons.forEach(function(button) {
        button.addEventListener('click', function(){
            console.log(button.dataset['joinkey'])
            socket.emit('join_chat', {'join_key': button.dataset['joinkey']});
        });
    });
    socket.on('joined', function(data) {
        console.log('joined to room', data);
        //wait 10s 
        window.location.href = '/chat';
    });

    function handle_user_name_form() {
        return new Promise((resolve, reject) => {
            document.getElementById('lightbox-user-name').classList.add('active');

            const user_name_form = document.getElementById('user-name-form');
            user_name_form.addEventListener('submit', function(event) {
                event.preventDefault();
                console.log("Submit");
                const formData = new FormData(user_name_form);
                const action = user_name_form.getAttribute('action');

                    fetch(action, {
                        method: 'POST',
                        body: formData
                    }).then(response => response.json()).then(data => {

                        document.getElementById('lightbox-user-name').classList.remove('active');
                        console.log("Serwer mi oddał takie dane: ", data);
                        user_name = data.user_name;
                        already_logged_in = user_name != '';
                        resolve();
                    }).catch(error => {
                        console.error('Error:', error);
                        reject(error);
                    });
                });
        });
    }

    random_pairing_button.addEventListener('click', function() {
        console.log('random pairing');
        if (!already_logged_in){
            handle_user_name_form().then(() => {
                console.log("Dalej")
                document.getElementById('lightbox-pairing').classList.add('active');
            }).catch((error) => {
                console.log("Error: ", error);
            });
        }else{
            document.getElementById('lightbox-pairing').classList.add('active');
        }
    });

    connect_direct_button.addEventListener('click', function() {
        console.log('connect direct');
        if (!already_logged_in){
            handle_user_name_form().then(() => {
                document.getElementById('lightbox-connect-direct').classList.add('active');
            });
        }else{
            document.getElementById('lightbox-connect-direct').classList.add('active');
        }
    });

    create_room_button.addEventListener('click', function() {
        console.log('create room');
        if (!already_logged_in){
            handle_user_name_form().then(() => {
                document.getElementById('lightbox-create-room').classList.add('active');
            });
        }else{
            document.getElementById('lightbox-create-room').classList.add('active');
        }
    });

    your_rooms_button.addEventListener('click', function() {
        console.log('your rooms');
        document.getElementById('lightbox-rooms-list').classList.add('active');
    });

    settings_button.addEventListener('click', function() {
        console.log('settings');
    });


});