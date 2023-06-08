let db;

let dbReady = new Promise((resolve, reject) => {
    let openRequest = indexedDB.open("IceBreakerDatabase", 1);

    openRequest.onupgradeneeded = function(e) {
        var db = e.target.result;

        if (!db.objectStoreNames.contains('messages')) {
            var storeOS = db.createObjectStore('messages', { keyPath: 'message_id', unique: true});
            storeOS.createIndex('room', 'room', { unique: false });
        }
    };

    openRequest.onsuccess = function(e) {
        console.log("onupgradeneeded success");
        db = e.target.result;
        resolve();
    };

    openRequest.onerror = function(e) {
        console.log("onupgradeneeded error", e.target.error.name);
        console.log(e);
        reject();
    };
});

function addMessageToDB(message_id, room, content_type, content, time, timestamp, author, author_id, sender){
    const transaction = db.transaction(['messages'], 'readwrite');
    const store = transaction.objectStore('messages');
    console.log("addMessageToDB data:", {"message_id": message_id, "room": room, "content_type": content_type, "content": content, "time": time, "timestamp": timestamp, "author": author, "sender": sender});
    var message = {
        message_id: message_id,
        room: room,
        content_type: content_type,
        content: content,
        time: time,
        timestamp: timestamp,
        author: author,
        author_id: author_id,
        sender: sender
    };

    var request = store.add(message);

    request.onerror = function(e) {
        console.log("addMessageToDB error", e.target.error.name);
        console.log(e);
    };

    request.onsuccess = function(e) {
        console.log("addMessageToDB success");
    };
}

function getMessagesFromDB(room){
    return new Promise((resolve, reject) => {
        var transaction = db.transaction(['messages'], 'readonly');
        var store = transaction.objectStore('messages');
        var index = store.index('room');

        var request = index.getAll(IDBKeyRange.only(room));

        request.onerror = function(e) {
            console.log("getMessagesFromDB error", e.target.error.name);
            console.log(e);
            reject(e);
        };

        request.onsuccess = function(e) {
            let messages = e.target.result;
            resolve(messages);
        };
    });
}

function updateMessageTimeInDB(data){
    return new Promise((resolve, reject) => {
        var transaction = db.transaction(['messages'], 'readwrite');
        var store = transaction.objectStore('messages');
        var request = store.get(data.message_id);
        console.log("updateMessageTimeInDB data:", data);

        request.onerror = function(e) {
            console.log("updateMessageTime error", e.target.error.name);
            console.log(e);
            reject(e);
        };

        request.onsuccess = function(e) {
            const message = e.target.result;
            console.log("updateMessageTime message from DB:", message);
            message.time = data.time;
            message.timestamp = data.timestamp;
            var requestUpdate = store.put(message);
            requestUpdate.onerror = function(e) {
                console.log("updateMessageTime put error", e.target.error.name);
                reject(e);
            }
            requestUpdate.onsuccess = function() {
                console.log("updateMessageTime put success");
                console.log("updateMessageTime time:", message.time)
                resolve(message.time);
            }
        }
    });
}