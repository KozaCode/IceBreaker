document.addEventListener('DOMContentLoaded', function() {
    console.log('wait_script.js loaded');
    let timer;
    const socket = io();
    socket.emit('pair');
    socket.on('paired', function() {
        console.log("Paired");
        clearTimeout(timer);
        window.location.href = '/chat';
        socket.emit('join_chat', {"Room": "<ROOM_ID>"}); // TODO: Determine room id
    });
    socket.on('joined', function(data) {
        console.log('joined');
        window.location.href = '/chat';
    });
    socket.on('no_match_yet', function(data) {
        console.log('no match yet');
        document.getElementById('progress-bar').classList.add('animate');
        timer = setTimeout(function() {
            document.getElementById('progress-bar').classList.remove('animate');
            socket.emit('pair');
        }, 10000);
    });

});