from selenium.webdriver.chrome.options import Options
from selenium import webdriver

from flask import Flask, render_template, request, jsonify
from flask_caching import Cache
from termcolor import colored
from time import sleep
from PIL import Image
from io import BytesIO
import base64
import os 
import stat


app = Flask(__name__)

cache = Cache()

cache.init_app(app, config={'CACHE_TYPE': 'SimpleCache'})


st = os.stat('chromedriver') # linux specific
os.chmod('chromedriver', st.st_mode | stat.S_IEXEC)

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--hide-scrollbars")


@app.route('/')
@cache.cached(timeout=86400)
def home():
    return render_template('index.html')


@app.route('/gen')
@cache.cached(timeout=3600, query_string=True)
def gen_image():   
		try: 
			driver = webdriver.Chrome('chromedriver', options=chrome_options)

			# 1) Open website, wait a second to load & take screenshot with selenium in headless mode
			protocol = "http://" 

			_website = str(request.args.get("website"))  # the argument is not gonna be in string  
			if not "http" in _website: 
				website = protocol + _website 
			else:
				website = _website

			# 2) Save the screenshot as ss.png & close the browser
			file_name = "ss.png"

			driver.set_window_size(1614, 828)

			driver.get(website)
			sleep(1) # wait for the page to load

			driver.get_screenshot_as_file(file_name)
			driver.quit()

			# 3) Open mockup file with PIL & overlay the screenshot in the coords of placeholder
			mockup = Image.open('./static/images/mockup.png')
			ss = Image.open(file_name)
			mockup.paste(ss, (153, 160)) 

			# 4) Now delete the screenshot to save space & then save the overlayed mockup as bytes 
			os.remove(file_name)

			buffered = BytesIO()
			mockup.save(buffered, format="PNG")

			# 5) Encode the bytes to base64 and return it in json format
			img_str = base64.b64encode(buffered.getvalue())

			response = jsonify(img=str(img_str))

		except Exception as error:

			# print(colored("ERROR - \n", red), error)
			print("ERROR - \n", error)

			driver.quit()

			response =  jsonify(error="Error Occurred")

		response.headers.add("Access-Control-Allow-Origin", "*")
		
		return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)

## Brain Storming & Project Breakdown

# 1) Open website, wait a second to load & take screenshot with selenium in headless mode
# 2) Save the screenshot as ss.png & close the browser
# 3) Open mockup file with PIL & overlay the screenshot in the coords of placeholder
# 4) Now delete the screenshot to save space & then save the overlayed mockup as bytes 
# 5) Encode the bytes to base64 and return it in json format

## TODO 
# 1) Setup a wsgi production server ✅
# 2) Caching for recently requested websites  