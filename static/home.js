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
    if (cropState.firstTime == true) {
        streamResolution.x = videoStreamID.videoWidth;
        streamResolution.y = videoStreamID.videoHeight;
        fullCanvas.width = streamResolution.x;
        fullCanvas.height = streamResolution.y;
        cropState.firstTime = false;
    }

    if (cropState.endSelection == false) {
        selectionStart.x = event.offsetX * streamResolution.x / 960;
        selectionStart.y = event.offsetY * streamResolution.y / 600;
        cropState.endSelection = true;
    }
    else {
        cropAndProcessImage(selectionStart.x, selectionStart.y, (event.offsetX * streamResolution.x / 960) - selectionStart.x, (event.offsetY * streamResolution.y / 600) - selectionStart.y);
        cropState.endSelection = false;
    }
}


const videoStreamID = document.getElementById('video-stream');

const fullCanvas = document.createElement('canvas');

const croppedCanvas = document.createElement('canvas');

const textOutputID = document.getElementById('text-output');

videoStreamID.addEventListener('click', userSelectedArea);

var streamResolution = {x: undefined, y: undefined};

var cropState = {firstTime: true, endSelection: false};

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
