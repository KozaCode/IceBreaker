document.addEventListener('DOMContentLoaded', function() {
    let random_pairing_button = document.getElementById('random-pairing');
    let connect_direct_button = document.getElementById('connect-direct');
    let create_room_button = document.getElementById('create-room');
    let your_rooms_button = document.getElementById('your-rooms');
    let settings_button = document.getElementById('settings');

    random_pairing_button.addEventListener('click', function() {
        window.location.href = '/random-form';
    });
    connect_direct_button.addEventListener('click', function() {
        window.location.href = '/connect-direct';
    });
    create_room_button.addEventListener('click', function() {
        window.location.href = '/create-room';
    });
    your_rooms_button.addEventListener('click', function() {
        window.location.href = '/your-rooms';
    });
    settings_button.addEventListener('click', function() {
        window.location.href = '/settings';
    });
});