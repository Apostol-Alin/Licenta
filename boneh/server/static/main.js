function startCountdown(duration) {
    const timerElement = document.getElementById('countdown');
    if (duration <= 0) {
        timerElement.innerText = '0:00';
        return;
    }
    
    function updateTimer() {
        if (duration <= 0) {
            timerElement.innerText = '0:00';
            clearInterval(interval);
        } else {
            let minutes = Math.floor(duration / 60);
            let seconds = duration % 60;
            timerElement.innerText = `${minutes}:${seconds.toString().padStart(2, '0')}`;
            duration--;
        }
    }
    
    updateTimer();
    const interval = setInterval(updateTimer, 1000);
}
