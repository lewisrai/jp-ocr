function cropAndProcessImage(x, y, width, height) {
    fullCanvas.getContext('2d').drawImage(videoStreamID, 0, 0);

    croppedCanvas.width = width;
    croppedCanvas.height = height;
    croppedCanvas.getContext('2d').drawImage(fullCanvas, x, y, width, height, 0, 0, width, height);

    $.ajax({
        type: "POST",
        url: "/process",
        data: {
            imageBase64: croppedCanvas.toDataURL()
        },
        success: function(response) {
            textOutputID.innerHTML = response;
        }
    })
}


function userSelectedArea(event) {
    const select = {x: event.offsetX * streamResolution.x / 960, y: event.offsetY * streamResolution.y / 600}


    if (endSelection == false) {
        selectionStart.x = select.x;
        selectionStart.y = select.y;
        endSelection = true;
    }
    else {
        cropAndProcessImage(selectionStart.x, selectionStart.y, select.x, select.y);
        endSelection = false;
    }
}


function streamStarts(event) {
    streamResolution.x = videoStreamID.videoWidth;
    streamResolution.y = videoStreamID.videoHeight;
    fullCanvas.width = streamResolution.x;
    fullCanvas.height = streamResolution.y;
}


const videoStreamID = document.getElementById('video-stream');

const fullCanvas = document.createElement('canvas');

const croppedCanvas = document.createElement('canvas');

const textOutputID = document.getElementById('text-output');

var streamResolution = {x: undefined, y: undefined};

var endSelection = false;

var selectionStart = {x: undefined, y: undefined};

navigator.mediaDevices.getDisplayMedia({
    audio: false,
    video: {
        width: {
            ideal: 2560
        },
        height: {
            ideal: 1600
        },
        framerate: {
            max: 5
        }
    }
}).then(stream => {
    videoStreamID.srcObject = stream;
}).catch(console.error);

videoStreamID.addEventListener('click', userSelectedArea);

videoStreamID.addEventListener('play', streamStarts);
