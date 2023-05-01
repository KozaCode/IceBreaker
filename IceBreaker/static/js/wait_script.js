document.addEventListener('DOMContentLoaded', function() {
    const socket = io();
    socket.emit('pair');
    socket.on('paired', function(data) {
        window.location.href = '/chat';
    });
    socket.on('no_match_yet', function(data) {
        //wait and resend pair
        setTimeout(function() {
            socket.emit('pair');
        }, 10000)
    });
});