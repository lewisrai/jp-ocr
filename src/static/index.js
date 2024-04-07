async function processImage(x, y, width, height) {
    croppedCanvas.width = videoStreamID.videoWidth;
    croppedCanvas.height = videoStreamID.videoHeight;
    croppedCanvas.getContext("2d").drawImage(videoStreamID, 0, 0);

    const response = await fetch("http://127.0.0.1:5000/api", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: croppedCanvas.toDataURL(),
    });

    const data = await response.json();

    console.log(data);
}

const videoStreamID = document.getElementById("video-stream");

const croppedCanvas = document.createElement("canvas");

navigator.mediaDevices
    .getDisplayMedia({
        audio: false,
        video: {
            width: {
                ideal: 2560,
            },
            height: {
                ideal: 1600,
            },
            framerate: {
                max: 5,
            },
        },
    })
    .then((stream) => {
        videoStreamID.srcObject = stream;
    });

videoStreamID.addEventListener("click", processImage);
