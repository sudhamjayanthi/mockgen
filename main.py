from selenium.webdriver.chrome.options import Options
from selenium import webdriver

from flask import Flask, render_template, request, jsonify
from time import sleep
from PIL import Image
from io import BytesIO
import base64
import os 

app = Flask(__name__)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--hide-scrollbars")


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/gen')
def gen_image():   
    try: 
        # 1) Open website, wait a second to load & take screenshot with selenium in headless mode
        protocol = "http://" 

        _website = str(request.args.get("website"))  # the argument is not gonna be in string  
        if not "http" in _website: 
            website = protocol + _website 
        else:
            website = _website

        # 2) Save the screenshot as ss.png & close the browser
        file_name = "ss.png"

        driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)
        driver.set_window_size(1614, 828)
        
        print(website)
        driver.get(website)

        sleep(1) # wait for the page to load
        driver.get_screenshot_as_file(file_name)
        driver.quit()

        # 3) Open mockup file with PIL & overlay the screenshot in the coords of placeholder
        mockup = Image.open('mockup.png')
        ss = Image.open(file_name)
        mockup.paste(ss, (153, 160)) 

        # 4) Now delete the screenshot to save space & then save the overlayed mockup as bytes 
        os.remove(file_name)

        buffered = BytesIO()
        mockup.save(buffered, format="PNG")

        # 5) Encode the bytes to base64 and return it in json format
        img_str = base64.b64encode(buffered.getvalue())
  
        return jsonify(img=str(img_str))
    except Exception as e:
        print("Error occured -> \n", e)
        return jsonify(error="Error Occurred")

 
if __name__ == '__main__':
    app.run(debug=True)


# Project Breakdown into smaller steps
# 1) Open website, wait a second to load & take screenshot with selenium in headless mode
# 2) Save the screenshot as ss.png & close the browser
# 3) Open mockup file with PIL & overlay the screenshot in the coords of placeholder
# 4) Now delete the screenshot to save space & then save the overlayed mockup as bytes 
# 5) Encode the bytes to base64 and return it in json format