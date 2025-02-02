const chatLeftside = document.querySelector('.chat-leftsidebar');
const userChat = document.querySelector('.user-chat');
const mobileBottomNavigation = document.querySelector('.mobile-bottom-navigation');
const messageInput = document.getElementById('message-input');
const loggedUserId = document.querySelector('meta[name="logged-user"]').getAttribute('content');
const messageList = document.getElementById('message-list');
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
const sendBtn = document.getElementById("send");
const currentPartnerName = document.getElementById('current-partner-name');
const currentPartnerAvatar = document.getElementById('current-partner-avatar');
const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
let activeSockets = {};
let currentRoom = null;

const deactivateConversation = () => {
    const currentActiveRoom = document.querySelector('li.active');
    if (currentActiveRoom) {
        currentActiveRoom.classList.remove('active');
    }
}

const openChat = () => {
    chatLeftside.style.display = 'none';
    userChat.style.display = 'block';
    mobileBottomNavigation.style.display = 'none';
    messageInput.classList.add('mobile-bottom-navigation');
}

const closeChat = () => {
    chatLeftside.style.display = 'block';
    userChat.style.display = 'none';
    mobileBottomNavigation.style.display = 'flex';
    messageInput.classList.remove('mobile-bottom-navigation');
    deactivateConversation();
}

const scrollToBottom = () => {
    const chatBox = document.getElementById("message-list");
    chatBox.scrollTop = chatBox.scrollHeight;
}

const createLeftChatItem = (user) => {
    const li = document.createElement('li');
    li.className = 'left';

    const receivedMessageDiv = document.createElement('div');
    receivedMessageDiv.className = 'message received';

    const metadataDiv = document.createElement('span');
    metadataDiv.className = 'metadata';

    const timeSpan = document.createElement('span');
    timeSpan.className = 'time';
    timeSpan.textContent = user.time;

    metadataDiv.appendChild(timeSpan);

    receivedMessageDiv.textContent = user.message;
    receivedMessageDiv.appendChild(metadataDiv);
    li.appendChild(receivedMessageDiv);

    return li;
}

const createRightChatItem = (user) => {
    const li = document.createElement('li');
    li.className = 'right';

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message sent';

    const metadataDiv = document.createElement('span');
    metadataDiv.className = 'metadata';

    const timeSpan = document.createElement('span');
    timeSpan.className = 'time';
    timeSpan.textContent = user.time;

    metadataDiv.appendChild(timeSpan);

    messageDiv.textContent = user.message;
    messageDiv.appendChild(metadataDiv);
    li.appendChild(messageDiv);

    return li;
}

async function listAllMessage(conversation_id, user) {
    currentPartnerName.innerText = user.name;
    currentPartnerAvatar.src = user.avatar;

    try {
        const response = await fetch('/api/load-messages', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({ conversation_id })
        });

        if (!response.ok) throw new Error('Failed to fetch messages');

        const data = await response.json();
        const messages = data.messages;
        messageList.innerHTML = '';
        messages.forEach(element => {
            let messageHTML = '';
            if (element.sender_id == loggedUserId) {
                messageHTML = createRightChatItem({
                    message: element.content,
                    time: "10:02"
                });
            } else {
                messageHTML = createLeftChatItem({
                    message: element.content,
                    time: "12:09",
                });
            }

            messageList.appendChild(messageHTML);
        });

        scrollToBottom();

    } catch (error) {
        console.error('Error:', error);
    }
}

const loadMessage = (event) => {
    messageList.innerHTML = '';
    const partnerAvatar = event.querySelector('img').src;
    const partnerFullName = event.querySelector('#full-name').innerText;
    let roomId = event.getAttribute("data-room");

    listAllMessage(roomId, {
        name: partnerFullName,
        avatar: partnerAvatar
    });

    deactivateConversation();
    event.classList.add('active');

    if (currentRoom !== null && activeSockets[currentRoom]) {
        activeSockets[currentRoom].close();
    }

    const socket = new WebSocket(`${protocol}${window.location.host}/ws/message/${roomId}/`);
    activeSockets[roomId] = socket;
    currentRoom = roomId;

    socket.onmessage = function (e) {
        let data = JSON.parse(e.data);
        messageHTML = '';
        if (data.sender_id == loggedUserId) {
            messageHTML = createRightChatItem({
                name: data.full_name,
                message: data.message,
                time: "10:02"
            });
        } else {
            messageHTML = createLeftChatItem({
                name: partnerFullName,
                message: data.message,
                time: "12:09",
                avatar: partnerAvatar
            })
        }

        messageList.appendChild(messageHTML);
        scrollToBottom();
    };

    sendBtn.addEventListener("click", function () {
        const message = document.getElementById("message");
        socket.send(JSON.stringify({ "message": message.value, "sender": loggedUserId }));
        message.value = '';
        message.focus();
    });

    if (window.innerWidth < 992) {
        openChat();
    }
}

document.getElementById('message-input').addEventListener('keypress', function (event) {
    if (event.key === 'Enter') {
        sendBtn.click();
    }
});