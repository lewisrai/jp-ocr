async function processImage(x, y, width, height) {
    croppedCanvas.width = width;
    croppedCanvas.height = height;
    croppedCanvas
        .getContext("2d")
        .drawImage(videoStreamID, x, y, width, height, 0, 0, width, height);

    const response = await fetch("http://127.0.0.1:5000/api/", {
        method: "POST",
        headers: {
            "Content-Type": "text/plain",
        },
        body: croppedCanvas.toDataURL(),
    });

    const text = await response.text();

    textOutputID.innerHTML = text;
}

function markPositions(event) {
    const select = {
        x: Math.trunc((event.offsetX * videoStreamID.videoWidth) / 960),
        y: Math.trunc((event.offsetY * videoStreamID.videoHeight) / 600),
    };

    if (setPosition1) {
        position1.x = select.x;
        position1.y = select.y;
        setPosition1 = false;
    } else {
        position2.x = select.x;
        position2.y = select.y;
        setPosition1 = true;
    }

    positionsID.innerHTML = `Top Left: ${position1.x}, ${position1.y} - Bottom Right: ${position2.x}, ${position2.y}`;
}

function callAPI() {
    const width = position2.x - position1.x;
    const height = position2.y - position1.y;

    if (width > 0 && height > 0) {
        processImage(position1.x, position1.y, width, height);
    }
}

window.onload = async () => {
    croppedCanvas = document.createElement("canvas");

    positionsID = document.getElementById("positions");

    textOutputID = document.getElementById("text-output");

    videoStreamID = document.getElementById("video-stream");

    videoStreamID.srcObject = await navigator.mediaDevices.getDisplayMedia({
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
    });

    videoStreamID.addEventListener("click", markPositions);
};

let croppedCanvas;

let videoStreamID;

const position1 = { x: 0, y: 0 };
const position2 = { x: 0, y: 0 };

let setPosition1 = true;
