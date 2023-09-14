const video = document.getElementById('videoMirror');


function startVideoMirror() {
    navigator.mediaDevices.getDisplayMedia({
        audio: false,
        video: true
    }).then(stream => {
        console.log("Successfully capturing screen!");
        video.srcObject = stream;
    }).catch(console.error)
}


var scratchCanvas = document.getElementById('imageCanvas');
var context = scratchCanvas.getContext('2d');

context.fillStyle = "blue"
context.fillRect(0, 0, 1280, 720);

var dataURL = scratchCanvas.toDataURL();


function sendImageForProcess() {
    console.log("Sending Captured Screenshot for OCR");

    $.ajax({
        type: "POST",
        url: "/process",
        data:{
            imageBase64: dataURL
        }
    }).done(function() {
            console.log("Sent!");
    })
}


//startVideoMirror()
//sendImageForProcess()
