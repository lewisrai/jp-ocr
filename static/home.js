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
                max: 15
            }
        }
    }).then(stream => {
        videoStreamID.srcObject = stream;
        console.log("INFO: Successfully Capturing Screen");
    }).catch(console.error)
}


function cropAndProcessImage(x, y, width, height) {
    console.log("INFO: Cropping User Selection");

    fullCanvas.getContext('2d').drawImage(videoStreamID, 0, 0);

    croppedCanvas.width = width;
    croppedCanvas.height = height;
    croppedCanvas.getContext('2d').drawImage(fullCanvas, x, y, width, height, 0, 0, width, height);

    displayedCanvasID.getContext('2d').drawImage(croppedCanvas, 0, 0, width, height, 0, 0, displayedCanvasID.width, displayedCanvasID.height);

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


function userSelectedArea(event) {
    if (firstTime == true) {
        streamResolutionX = videoStreamID.videoWidth;
        streamResolutionY = videoStreamID.videoHeight;
        fullCanvas.width = streamResolutionX;
        fullCanvas.height = streamResolutionY;
        console.log("INFO: Stream Resolution: " + streamResolutionX + "x" + streamResolutionY);
        firstTime = false;
    }

    if (secondSelectionClick == false) {
        selectionStartX = event.offsetX * streamResolutionX / 640;
        selectionStartY = event.offsetY * streamResolutionY / 400;
        secondSelectionClick = true;
    }
    else {
        cropAndProcessImage(selectionStartX, selectionStartY, (event.offsetX * streamResolutionX / 640) - selectionStartX, (event.offsetY * streamResolutionY / 400) - selectionStartY);
        secondSelectionClick = false;
    }
}


const videoStreamID = document.getElementById('videoStream');

const fullCanvas = document.createElement('canvas');

const croppedCanvas = document.createElement('canvas');

const displayedCanvasID = document.getElementById('displayedCanvas');

const textOutputID = document.getElementById('textOutput');

startVideoStream()

videoStreamID.addEventListener('click', userSelectedArea);

var streamResolutionX = undefined;

var streamResolutionY = undefined;

var firstTime = true;

var secondSelectionClick = false;

var selectionStartX = undefined;

var selectionStartY = undefined;

console.log("INFO: Initialised");
