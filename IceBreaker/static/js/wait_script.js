document.addEventListener('DOMContentLoaded', function() {
    const socket = io();
    socket.emit('pair');
    socket.on('paired', function(data) {
        window.location.href = '/chat';
    });
});