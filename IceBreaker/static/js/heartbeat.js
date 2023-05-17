const socket = io();
socket.on('are_you_alive', function(data){
    socket.emit('pulse');
    console.log('pulse');
});