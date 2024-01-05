function cropAndProcessImage(x, y, width, height) {
    croppedCanvas.width = width;
    croppedCanvas.height = height;
    croppedCanvas.getContext('2d').drawImage(videoStreamID, x, y, width, height, 0, 0, width, height);

    $.ajax({
        type: "POST",
        url: "/api",
        data: {
            imageBase64: croppedCanvas.toDataURL()
        },
        success: function(response) {
            textOutputID.innerHTML = response;
        }
    })
}


function userSelectedArea(event) {
    const select = {x: event.offsetX * videoStreamID.videoWidth / 960, y: event.offsetY * videoStreamID.videoHeight / 600}

    if (endSelection == false) {
        selectionStart.x = select.x;
        selectionStart.y = select.y;
        endSelection = true;
    }
    else {
        cropAndProcessImage(selectionStart.x, selectionStart.y, select.x - selectionStart.x, select.y - selectionStart.y);
        endSelection = false;
    }
}


const videoStreamID = document.getElementById('video-stream');

const textOutputID = document.getElementById('text-output');

const croppedCanvas = document.createElement('canvas');

const selectionStart = {x: undefined, y: undefined};

var endSelection = false;

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
