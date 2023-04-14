document.addEventListener('DOMContentLoaded', function() {
    const socket = io();
    console.log("Paired");
    document.getElementById('user-id').innerHTML = data.user_id;
    document.getElementById('user-name').innerHTML = data.user_name;
    document.getElementById('partner-id').innerHTML = data.partner_id;
    document.getElementById('partner-name').innerHTML = data.partner_name;
});

