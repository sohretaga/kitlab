const chatLeftside = document.querySelector('.chat-leftsidebar');
const userChat = document.querySelector('.user-chat');
const mobileBottomNavigation = document.querySelector('.mobile-bottom-navigation');
const messageInput = document.getElementById('message-input');

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

const loadMessage = () => {
    if (window.innerWidth < 992) {
        openChat();
    } else {
        
    }
}