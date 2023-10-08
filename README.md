# JP-OCR
A web server built in Flask that captures the screen of applications to read text allowing you to translate using Yomichan inside a web browser. Supports only windows.

## Running JP-OCR
#### First Time
Open the config.yml file and change the value `use_local_model: True` to `use_local_model: False` and run it once to download the model. Once it has launched, close the console using *Control C* and reverse the above change. Go to your user directory:
`C:\Users\%USERPROFILE%\cache\huggingface\hub\models--kha-white--manga-ocr-base\snapshots`
rename the folder inside to *OCRModel* and copy the folder and place it inside the same folder as **main.py**.
#### Once Setup
Run the bat file to run the code. To create a shortcut, use the bat file as the program to run from the shortcut.

## Dependencies
[Python 3](https://www.python.org/downloads/) must be installed with the following dependencies: flask and manga-ocr using pip3. These will also have dependencies.
`pip3 install flask`
`pip3 install manga-ocr`

## Thanks
Thanks to [manga-ocr](https://github.com/kha-white/manga-ocr) for making this project possible.
