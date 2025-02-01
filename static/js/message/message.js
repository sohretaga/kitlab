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
let activeSockets = {};
let currentRoom = null;

const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";

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
}

const scrollToBottom = () => {
    const chatBox = document.getElementById("message-list");
    chatBox.scrollTop = chatBox.scrollHeight;
}

const createLeftChatItem = (user) => {
    const li = document.createElement('li');

    const conversationList = document.createElement('div');
    conversationList.className = 'conversation-list';

    const chatAvatar = document.createElement('div');
    chatAvatar.className = 'chat-avatar';
    const img = document.createElement('img');
    img.src = user.avatar;
    img.alt = user.name;
    chatAvatar.appendChild(img);

    const ctextWrap = document.createElement('div');
    ctextWrap.className = 'ctext-wrap';

    const conversationName = document.createElement('div');
    conversationName.className = 'conversation-name';
    conversationName.textContent = user.name;

    const ctextWrapContent = document.createElement('div');
    ctextWrapContent.className = 'ctext-wrap-content';
    const messageParagraph = document.createElement('p');
    messageParagraph.className = 'mb-0';
    messageParagraph.textContent = user.message;
    ctextWrapContent.appendChild(messageParagraph);

    const chatTime = document.createElement('p');
    chatTime.className = 'chat-time mb-0';
    chatTime.innerHTML = `<i class="mdi mdi-clock-outline align-middle mr-1"></i> ${user.time}`;

    ctextWrap.appendChild(conversationName);
    ctextWrap.appendChild(ctextWrapContent);
    ctextWrap.appendChild(chatTime);
    conversationList.appendChild(chatAvatar);
    conversationList.appendChild(ctextWrap);
    li.appendChild(conversationList);

    return li;
}

const createRightChatItem = (user) => {
    const li = document.createElement('li');
    li.className = 'right';

    const conversationList = document.createElement('div');
    conversationList.className = 'conversation-list';

    const ctextWrap = document.createElement('div');
    ctextWrap.className = 'ctext-wrap';

    const conversationName = document.createElement('div');
    conversationName.className = 'conversation-name';
    conversationName.textContent = user.name;

    const ctextWrapContent = document.createElement('div');
    ctextWrapContent.className = 'ctext-wrap-content';
    const messageParagraph = document.createElement('p');
    messageParagraph.className = 'mb-0';
    messageParagraph.textContent = user.message;
    ctextWrapContent.appendChild(messageParagraph);

    const chatTime = document.createElement('p');
    chatTime.className = 'chat-time mb-0';
    chatTime.innerHTML = `<i class="bx bx-time-five align-middle mr-1"></i> ${user.time}`;

    ctextWrap.appendChild(conversationName);
    ctextWrap.appendChild(ctextWrapContent);
    ctextWrap.appendChild(chatTime);
    conversationList.appendChild(ctextWrap);
    li.appendChild(conversationList);

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
                    name: data.full_name,
                    message: element.content,
                    time: "10:02"
                });
            } else {
                messageHTML = createLeftChatItem({
                    name: user.name,
                    message: element.content,
                    time: "12:09",
                    avatar: user.avatar
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

    const currentActiveRoom = document.querySelector('li.active');
    if (currentActiveRoom) {
        currentActiveRoom.classList.remove('active');
    }

    event.classList.add('active');

    if (roomId === currentRoom) {
        return;
    }

    if (currentRoom !== null && activeSockets[currentRoom]) {
        activeSockets[currentRoom].close();
    }

    const socket = new WebSocket(`${protocol}${window.location.host}/ws/message/${roomId}/`);
    activeSockets[roomId] = socket;
    currentRoom = roomId;

    socket.onmessage = function(e) {
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

    sendBtn.addEventListener("click", function() {
        const message = document.getElementById("message");
        socket.send(JSON.stringify({ "message": message.value, "sender": loggedUserId }));
        message.value = '';
        message.focus();
    });

    if (window.innerWidth < 992) {
        openChat();
    }
}

document.getElementById('message-input').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        sendBtn.click();
    }
});