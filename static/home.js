const video = document.getElementById('video');


function startScreenMirror() {
    navigator.mediaDevices.getDisplayMedia({
        audio: false,
        video: true
    }).then(stream => {
        video.srcObject = stream;
    }).catch(console.error)
}


startScreenMirror()
