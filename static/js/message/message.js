const chatLeftside = document.querySelector('.chat-leftsidebar');
const userChat = document.querySelector('.user-chat');
const mobileBottomNavigation = document.querySelector('.mobile-bottom-navigation');
const messageDiv = document.getElementById('message-input');
const message = document.getElementById("message");
const loggedUserId = document.querySelector('meta[name="logged-user"]').getAttribute('content');
const messageList = document.getElementById('message-list');
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
const sendBtn = document.getElementById("send");
const currentPartnerName = document.getElementById('current-partner-name');
const currentPartnerAvatar = document.getElementById('current-partner-avatar');
const headerMain = document.querySelector('.header-main');
const container = document.querySelector('.product-container').querySelector('.container');
const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
let activeSockets = {};
let currentRoom = null;

const sentTick = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="15" id="msg-dblcheck"><path d="M10.91 3.316l-.478-.372a.365.365 0 0 0-.51.063L4.566 9.88a.32.32 0 0 1-.484.032L1.892 7.77a.366.366 0 0 0-.516.005l-.423.433a.364.364 0 0 0 .006.514l3.255 3.185a.32.32 0 0 0 .484-.033l6.272-8.048a.365.365 0 0 0-.063-.51z" fill="#92a58c"/></svg>'
const deliveredTick = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="15" id="msg-dblcheck" x="2047" y="2061"><path d="M15.01 3.316l-.478-.372a.365.365 0 0 0-.51.063L8.666 9.88a.32.32 0 0 1-.484.032l-.358-.325a.32.32 0 0 0-.484.032l-.378.48a.418.418 0 0 0 .036.54l1.32 1.267a.32.32 0 0 0 .484-.034l6.272-8.048a.366.366 0 0 0-.064-.512zm-4.1 0l-.478-.372a.365.365 0 0 0-.51.063L4.566 9.88a.32.32 0 0 1-.484.032L1.892 7.77a.366.366 0 0 0-.516.005l-.423.433a.364.364 0 0 0 .006.514l3.255 3.185a.32.32 0 0 0 .484-.033l6.272-8.048a.365.365 0 0 0-.063-.51z" fill="#92a58c"/></svg>'
const readTick = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="15" id="msg-dblcheck-ack" x="2063" y="2076"><path d="M15.01 3.316l-.478-.372a.365.365 0 0 0-.51.063L8.666 9.88a.32.32 0 0 1-.484.032l-.358-.325a.32.32 0 0 0-.484.032l-.378.48a.418.418 0 0 0 .036.54l1.32 1.267a.32.32 0 0 0 .484-.034l6.272-8.048a.366.366 0 0 0-.064-.512zm-4.1 0l-.478-.372a.365.365 0 0 0-.51.063L4.566 9.88a.32.32 0 0 1-.484.032L1.892 7.77a.366.366 0 0 0-.516.005l-.423.433a.364.364 0 0 0 .006.514l3.255 3.185a.32.32 0 0 0 .484-.033l6.272-8.048a.365.365 0 0 0-.063-.51z" fill="#4fc3f7"/></svg>'

const getAzerbaijanISOTime = () => {
    const date = new Date();

    // Convert to Azerbaijan time by adding 4 hours to UTC time
    date.setUTCHours(date.getUTCHours() + 4);

    // Return in ISO 8601 format
    return date.toISOString();
}

const closeAllSoctets = () => {
    if (currentRoom !== null && activeSockets[currentRoom]) {
        activeSockets[currentRoom].close();
    }
}

const deactivateConversation = () => {
    const currentActiveRoom = document.querySelector('li.active');
    message.value = '';

    if (currentActiveRoom) {
        currentActiveRoom.classList.remove('active');
    }

    closeAllSoctets();
}

const openChat = () => {
    container.style.padding = '0';
    headerMain.style.display = 'none';
    chatLeftside.style.display = 'none';
    userChat.style.display = 'block';
    mobileBottomNavigation.style.display = 'none';
    messageDiv.classList.add('mobile-bottom-navigation');
}

const closeChat = () => {
    container.style.padding = '0 15px';
    headerMain.style.display = '';
    chatLeftside.style.display = 'block';
    userChat.style.display = 'none';
    mobileBottomNavigation.style.display = 'flex';
    messageDiv.classList.remove('mobile-bottom-navigation');
    deactivateConversation();
}

const scrollToBottom = () => {
    const chatBox = document.getElementById("message-list");
    chatBox.scrollTop = chatBox.scrollHeight;
}

const messageStatusHandler = (isRead, process) => {
    const span = document.createElement('span');

    if (process) {
        span.className = 'tick';
        span.innerHTML = sentTick;
    } else {
        span.className = isRead ? 'tick':'tick tick-animation';
        span.innerHTML = deliveredTick + readTick;
    }

    return span;
}

const messageRead = (message, read=false) =>{
	const tick = message.querySelector('.tick');
    if (tick && read) {
        setTimeout(() => {
            tick.classList.remove('tick-animation')
        }, 10);
    }
}

const formatDate = (timestamp) => {
    const date = new Date(timestamp);  
    const today = new Date(getAzerbaijanISOTime());
    const yesterday = new Date(getAzerbaijanISOTime());
    
    yesterday.setDate(today.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
        return "Bu gün";
    } else if (date.toDateString() === yesterday.toDateString()) {
        return "Dünən";
    } else {
        const options = { day: 'numeric', month: 'long', year: 'numeric' };
        let formattedDate = date.toLocaleDateString('az-AZ', options);
        return formattedDate.replace(/\b\p{L}/u, match => match.toUpperCase());
    }
}

const chatDayTitle = (timestamp) => {
    const chatDayId = timestamp.split("T")[0];

    if (!document.getElementById(chatDayId)) {
        const li = document.createElement('li');
        li.id = chatDayId;

        const div = document.createElement('div');
        div.className = 'chat-day-title';

        const span = document.createElement('span');
        span.className = 'title';
        span.textContent = formatDate(timestamp);

        div.appendChild(span);
        li.appendChild(div);

        messageList.appendChild(li);
    }
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
    timeSpan.textContent = user.timestamp.slice(11, 16); // HH:MM

    metadataDiv.appendChild(timeSpan);
    
    receivedMessageDiv.textContent = user.message;
    receivedMessageDiv.appendChild(metadataDiv);
    li.appendChild(receivedMessageDiv);

    return li;
}

const createRightChatItem = (user) => {
    const li = document.createElement('li');
    li.className = user.process ? 'right process':'right';

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message sent';

    const metadataDiv = document.createElement('span');
    metadataDiv.className = 'metadata';

    const timeSpan = document.createElement('span');
    timeSpan.className = 'time';
    timeSpan.textContent = user.timestamp.slice(11, 16); // HH:MM

    const tickSpan = messageStatusHandler(user.is_read, user.process);
    metadataDiv.appendChild(timeSpan);
    metadataDiv.appendChild(tickSpan);

    messageDiv.textContent = user.message;
    messageDiv.appendChild(metadataDiv);
    li.appendChild(messageDiv);

    return li;
}

const createChatBubble = (data) => {
    const messageBubble = document.getElementById('message-bubble');
    if (data.has_message) {
        if (!messageBubble) {
            const li = document.createElement('li');
            li.className = 'left';
            li.id = 'message-bubble';
    
            const receivedMessageDiv = document.createElement('div');
            receivedMessageDiv.className = 'message received';
    
            const typingDiv = document.createElement('div');
            typingDiv.className = 'typing';
    
            for (let i = 0; i < 3; i++) {
                const dot = document.createElement('div');
                dot.className = 'dot';
                typingDiv.appendChild(dot);
            }
    
            receivedMessageDiv.appendChild(typingDiv);
            li.appendChild(receivedMessageDiv);
            messageList.appendChild(li);
        }
    } else {
        messageBubble?.remove();
    }
}

const createDialogueBox = (data) => {
    let messageHTML = '';

    if (data.sender_id == loggedUserId) {
        const processMessages = document.querySelectorAll('.process');
        processMessages.forEach(messageHTML => {
            const tick = messageHTML.querySelector('.tick');
            tick.innerHTML = deliveredTick + readTick;
            tick.classList.add('tick-animation');
            messageHTML.classList.remove('process');
            messageRead(messageHTML, data.is_read);
        })

    } else {
        document.getElementById('message-bubble')?.remove();

        messageHTML = createLeftChatItem({
            message: data.message,
            timestamp: data.timestamp,
        });

        messageList.appendChild(messageHTML);
        messageRead(messageHTML, data.is_read);
    }
}

const makeMessageAsRead = () => {
    const ticks = document.querySelectorAll('.tick-animation');
    ticks.forEach(tick => {
        tick.className = 'tick';
    })
}

async function cleanUnreadMessages(li) {

    li.classList.remove('unread-messages');

    const newMessageCount = li.querySelector('.message-count');
    const unreadCount = parseInt(newMessageCount.textContent) || 0;

    const allNewMessageCount = document.querySelectorAll('.count');
    allNewMessageCount.forEach(count => {
        let currentCount = parseInt(count.textContent) || 0;
        let updatedCount = Math.max(currentCount - unreadCount, 0);
        
        count.textContent = updatedCount;
        if (updatedCount === 0) {
            count.style.display = 'none';
        }
    });

    newMessageCount.textContent = '';
}

async function sortConversationList (roomId, newId) {
    const conversation = document.querySelector(`li[data-room="${roomId}"]`);
    conversation.id = newId;

    const ul = document.getElementById("conversation-list");
    const items = Array.from(ul.querySelectorAll("li"));

    const sortItems = async () => {
        return items.sort((a, b) => {
            const idA = parseInt(a.id, 10);
            const idB = parseInt(b.id, 10);
            return idB - idA;
        });
    };
    const sortedItems = await sortItems();
    sortedItems.forEach(li => ul.appendChild(li));
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
            chatDayTitle(element.timestamp);

            if (element.sender_id == loggedUserId) {
                messageHTML = createRightChatItem({
                    message: element.content,
                    is_read: element.is_read,
                    timestamp: element.timestamp,
                    process: false
                });
            } else {
                messageHTML = createLeftChatItem({
                    message: element.content,
                    timestamp: element.timestamp,
                });
            }

            messageList.appendChild(messageHTML);
        });

        scrollToBottom();

    } catch (error) {
        console.error('Error:', error);
    }
}

function sendMessage() {
    const timestamp = getAzerbaijanISOTime();
    chatDayTitle(timestamp);

    messageHTML = createRightChatItem({
        message: message.value,
        timestamp: timestamp,
        process: true
    });
    messageList.appendChild(messageHTML);
    scrollToBottom();

    message_value = message.value;
    message.value = '';

    activeSockets[currentRoom].send(JSON.stringify({
        "type": "chat_message",
        "message": message_value,
        "sender": loggedUserId,
        "timestamp": timestamp
    }));

    message.focus();
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

    const socket = new WebSocket(`${protocol}${window.location.host}/ws/message/${roomId}/`);
    activeSockets[roomId] = socket;
    currentRoom = roomId;

    socket.onmessage = function (e) {
        let data = JSON.parse(e.data);

        if (data.type == "chat_typing" && data.sender_id != loggedUserId) {
            createChatBubble(data);
        }

        else if (data.type == "member_joined") {
            if (data.sender_id != loggedUserId) {
                makeMessageAsRead();
            } else {
                cleanUnreadMessages(event);
            }
        }

        else if (data.type == "chat_message") {
            createDialogueBox(data);
            sortConversationList(roomId, data.message_id);
        }

        scrollToBottom();
    };

    socket.onopen = function () {
        socket.send(JSON.stringify({
            "type": "member_joined",
            "sender": loggedUserId
        }));
    };

    sendBtn.removeEventListener("click", sendMessage); // remove old listener
    sendBtn.addEventListener("click", sendMessage);

    message.addEventListener("input", function() {
        const hasMessage = message.value ? true:false;

        socket.send(JSON.stringify({
            "type": "chat_typing",
            "has_message": hasMessage,
            "sender": loggedUserId
        }));
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