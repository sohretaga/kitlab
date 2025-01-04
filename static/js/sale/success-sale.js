var countdownTime = 9;

var countdownInterval = setInterval(function () {
    document.getElementById('countdown').innerText = countdownTime;
    countdownTime--;

    if (countdownTime < 0) {
        clearInterval(countdownInterval);
        window.location.replace('/')
    }
}, 1000);