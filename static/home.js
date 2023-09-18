function startVideoStream() {
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
                max: 30
            }
        }
    }).then(stream => {
        console.log("INFO: Successfully Capturing Screen");
        videoStreamID.srcObject = stream;
    }).catch(console.error)
}


function sendImageForProcess(x, y, width, height) {
    console.log("INFO: Cropping User Selection");

    fullCanvas.width = videoStreamID.videoWidth;
    fullCanvas.height = videoStreamID.videoHeight;
    fullCanvas.getContext('2d').drawImage(videoStreamID, 0, 0);

    croppedCanvas.width = width;
    croppedCanvas.height = height;
    croppedCanvas.getContext('2d').drawImage(fullCanvas, x, y, width, height, 0, 0, width, height);

    displayedCanvasID.getContext('2d').drawImage(croppedCanvas, 0, 0, width, height, 0, 0, 640, 400);

    const dataURL = croppedCanvas.toDataURL();

    console.log("INFO: Sending Cropped Screenshot For OCR");

    $.ajax({
        type: "POST",
        url: "/process",
        data: {
            imageBase64: dataURL
        },
        success: function(response) {
            textOutputID.innerHTML = response;
        }
    }).done(function() {
            console.log("INFO: AJAX Request Has Completed!");
    })
}


function cropSelectedArea(event) {
    if (secondClick == false) {
        selectionStartX = event.offsetX * 4;
        selectionStartY = event.offsetY * 4;
        secondClick = true;
    }
    else {
        sendImageForProcess(selectionStartX, selectionStartY, (event.offsetX * 4) - selectionStartX, (event.offsetY * 4) - selectionStartY);
    }
}


const videoStreamID = document.getElementById('videoStream');

const fullCanvas = document.createElement('canvas');

const croppedCanvas = document.createElement('canvas');

const displayedCanvasID = document.getElementById('displayedCanvas');

const textOutputID = document.getElementById('textOutput');

startVideoStream()

videoStreamID.addEventListener('click', cropSelectedArea);

var secondClick = false;

var selectionStartX = undefined;

var selectionStartY = undefined;

console.log("INFO: Initialised");
