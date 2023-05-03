# Optical Character Recognition using easyOCR 
#### Read data from a buisness card image using Optical Character Recognition(OCR) using easyOCR library and python and store the information in MySQL using mysql.connector
## How to run :
- Create a Virtual environment using requirements.txt file
- Create a local MySQL database using mysql.connector and create a table in the same database.(code to re-create the database and table can be found in database.py file)
- Run the python script "ocr_app.py" using this command: streamlit run twitter_scrape_app.py
- You will get a link to launch the webapp.
- Example images are provided in data folder.

## Features

- You can upload a buisness card image and view the extracted data, save the extracted data in a database.
- If you are not satisfied with the extracted data you can make changes in the extracted data and save updated data in the database.
- You can also delete unnecessary data.
