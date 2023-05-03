import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
import mysql.connector
from PIL import Image
import cv2
import os
import matplotlib.pyplot as plt
import re
import base64



def save_image(img):
    with open(os.path.join("uploaded_images", img.name), "wb") as f:
        f.write(img.getbuffer())


def encode_img(file):
    # Convert image data to binary format
    with open(file, 'rb') as file:
        binaryData = file.read()
        encodedData = base64.b64encode(binaryData)
    return encodedData

def extract_data(results):
    # extracting emails
    emails = list()
    for result in results:
        for text in result:
            if len(re.findall('\S+@\S+', text)) > 0:
                emails.append(re.findall('\S+@\S+', text))
    emails = [",".join(list(set(item))) for item in emails]

    # extracting phone numbers
    phone_regex = '(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}|\d{2}[-\.\s]??\d{3}[-\.\s]??\d{4})'
    phone_numbers = list()
    for result in results:
        current_phone_result = list()
        for text in result:
            number_list = re.findall(phone_regex, text)
            if len(number_list) > 0:
                # phone_numbers.append(number_list)
                for number in number_list:
                    if "-" in number:
                        current_phone_result.append(number)
        phone_numbers.append(current_phone_result)
    phone_numbers = [",".join(list(set(item))) for item in phone_numbers]

    # extracting urls
    def FindURL(string):
        from urlextract import URLExtract
        extractor = URLExtract()
        urls1 = extractor.find_urls(string)
        regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        url = re.findall(regex, string)
        urls2 = [x[0] for x in url]
        urls1.extend(urls2)
        return urls1

    urls = list()
    for result in results:
        current_result_urls = list()
        for text in result:
            url_list = FindURL(text)
            if len(url_list) > 0:
                current_result_urls.extend(url_list)
        urls.append(current_result_urls)
    urls = [",".join(list(set(url))) for url in urls]

    # extracting names and designations
    desig_keywords = ["DATA", "MANAGER", "CEO", "&", "FOUNDER", "General", "Manager", "Marketing",
                      "Executive", "Technical", "Manager"]
    names = list()
    designations = list()
    for result in results:
        first_line = result[0]
        name_parts = [item for item in first_line.split(" ") if item not in desig_keywords]
        name = " ".join(name_parts)
        designation_parts = [item for item in first_line.split(" ") if item not in name_parts]
        designation = " ".join(designation_parts)
        names.append(name)
        designations.append(designation)

    # Extracting company names
    company_names = list()
    for result in results:
        i = -1
        while True:
            temp = result[i]
            if temp not in urls and temp not in emails:
                company_names.append(temp)
                break
            i = i - 1

    # extracting areas
    areas = list()
    for result in results:
        for text in result:
            if re.findall('^[0-9].+, [a-zA-Z]+', text):
                areas.append(text.split(',')[0])
            elif re.findall('[0-9] [a-zA-Z]+', text):
                areas.append(text)

    # extracting cities
    cities = list()
    for result in results:
        for text in result:
            match1 = re.findall('.+St , ([a-zA-Z]+).+', text)
            match2 = re.findall('.+St,, ([a-zA-Z]+).+', text)
            match3 = re.findall('^[E].*', text)
            if match1:
                cities.append(match1[0])
            elif match2:
                cities.append(match2[0])
            elif match3:
                cities.append(match3[0])

    # extracting states
    states = list()
    for result in results:
        for text in result:
            state_match = re.findall('[a-zA-Z]{9} +[0-9]', text)
            if state_match:
                states.append(state_match[0].split(" ")[0])
            elif re.findall('^[0-9].+, ([a-zA-Z]+);', text):
                temp = text.split()[-3]
                state_name = re.sub(r'[^\w\s]', '', temp)
                states.append(state_name)

    # extracting pincodes
    pin_codes = list()
    for result in results:
        for text in result:
            pin_match = re.findall(r"(?<=[^_])\d{6,7}", text)
            if pin_match:
                pin_codes.append(pin_match[0])
    data = {}
    data["names"] = names
    data["designations"] = designations
    data["company_names"] = company_names
    data["emails"] = emails
    data["phone_numbers"] = phone_numbers
    data["urls"] = urls
    data["areas"] = areas
    data["cities"] = cities
    data["states"] = states
    data["pin_codes"] = pin_codes


    return data




st.markdown("<h1 style='text-align: center; color: yellow;'>Optical Character Recognition With easyOCR</h1>", unsafe_allow_html=True)

option = option_menu(None, ["App Info","easyOCR Demo","Modify Db", "View Data"],
                       default_index=0, orientation="horizontal")
if option == "App Info":
    st.subheader("easyOCR")
    st.write("EasyOCR is a Python library for Optical Character Recognition (OCR) that allows you to easily "
             "extract text from images and scanned documents.It takes the input as a printed or "
             "handwritten digital image and converts it to a digital text format that is machine-readable."
             "EasyOCR supports 42+ languages for detection purposes. EasyOCR is created by the company named Jaided AI company.")
    st.subheader("App Introduction")
    st.write("Using this App you can upload a business card image and it will detect all the relevant information"
             "on the app using easyOCR and python at backend. You can store this info with the image in a SQL Database."
             "If you think particular info is detected wrongly then you also have option to edit that info and save it"
             "in the Database. You can also delete unwanted info from the Database.")

if option == "easyOCR Demo":
    image_file = st.file_uploader("upload here",label_visibility="collapsed",type=["png","jpeg","jpg"])
    if image_file is not None:
        image = Image.open(image_file)
        st.image(image, caption='This is your image')
        save_image(image_file)
        saved_img = os.path.join(os.getcwd(),"uploaded_images",image_file.name)
        # INITIALIZING THE EasyOCR READER
        with st.spinner("Extracting..."):
            reader = easyocr.Reader(['en'])
            res = reader.readtext(saved_img, detail = 0, paragraph="False")
            da = extract_data([res])
            da_c = da.copy()
            da_c['image'] = encode_img(saved_img)
            df = pd.DataFrame(da)
            df_c = pd.DataFrame(da_c)
        st.success("Done!")
        if st.button("See Results"):
            st.table(df.T)
        if st.button("upload to db"):
            with st.spinner("Uploading to Db..."):
                mydb = mysql.connector.connect(host="localhost", user="root", password="mysql", database="ocr")
                mycursor = mydb.cursor(buffered=True)
                # mycursor.execute("SHOW TABLES")
                # for x in mycursor:
                #     st.write(x)
                for i, row in df_c.iterrows():
                    # here %S means string values
                    sql = """INSERT INTO ocr_data_2(card_holder_name,designation,company_name,email_address,mobile_number,
                    website_url,area,city,state,pin_code,image)
                                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                    mycursor.execute(sql, tuple(row))
                    # the connection is not auto committed by default, so we must commit to save our changes
                    mydb.commit()
            st.success("#### Uploaded to database successfully!")


if option == "Modify Db":
    mydb = mysql.connector.connect(host="localhost", user="root", password="mysql", database="ocr")
    mycursor = mydb.cursor(buffered=True)
    mycursor.execute("SELECT card_holder_name FROM ocr_data_2")
    result = mycursor.fetchall()
    names = tuple([result[i][0] for i in range(len(result))])
    selected_name = st.selectbox("Select a card holder name to update",names)
    st.write('### You selected:', selected_name)
    update_delete = option_menu("Select an Action", ["Update", "Delete"],default_index=0, orientation="horizontal")
    if update_delete == "Update":
        mycursor.execute(
            "select card_holder_name, designation, company_name, mobile_number,email_address,website_url,area,city,"
            "state,pin_code from ocr_data_2 WHERE card_holder_name=%s",(selected_name,))
        result2 = mycursor.fetchone()
        st.markdown("Input the value you want to change in corresponding field")
        card_holder_name = st.text_input("card_holder_name", result2[0])
        designation = st.text_input("designation", result2[1])
        company_name = st.text_input("company_name", result2[2])
        mobile_number = st.text_input("mobile_number", result2[3])
        email_address = st.text_input("email_address", result2[4])
        website_url = st.text_input("website_url", result2[5])
        area = st.text_input("area", result2[6])
        city = st.text_input("city", result2[7])
        state = st.text_input("state", result2[8])
        pin_code = st.text_input("pin_code", result2[9])
        if st.button("Make changes in Db"):
            mycursor.execute("""UPDATE ocr_data_2 SET card_holder_name=%s, designation=%s, company_name=%s, 
            mobile_number=%s,email_address=%s,website_url=%s,area=%s,city=%s,state=%s,pin_code=%s
                                            WHERE card_holder_name=%s""", (
            card_holder_name, designation, company_name, mobile_number, email_address, website_url, area, city, state, pin_code,
            selected_name))
            mydb.commit()
            st.success("Changes made in Db")

    elif update_delete == "Delete":
        st.write(f"#### press following button to delete the info of :red[**{selected_name}'**]")
        if st.button("Delete Business Card info"):
            mycursor.execute(f"DELETE FROM ocr_data_2 WHERE card_holder_name='{selected_name}'")
            mydb.commit()
            st.success("Business card information deleted from database.")

if option == "View Data":
    mydb = mysql.connector.connect(host="localhost", user="root", password="mysql", database="ocr")
    mycursor = mydb.cursor(buffered=True)
    mycursor.execute("SELECT card_holder_name FROM ocr_data_2")
    result = mycursor.fetchall()
    names = tuple([result[i][0] for i in range(len(result))])
    selected_name = st.selectbox("Select a card holder name to update", names)
    st.write('You selected:', selected_name)
    mycursor.execute(
        "select card_holder_name, designation, company_name, mobile_number,email_address,"
        "website_url,area,city,state,pin_code from ocr_data_2 where card_holder_name=%s", (selected_name,))
    updated_df = pd.DataFrame(mycursor.fetchall(),
                              columns=["card_holder_name", "designation", "company_name", "mobile_number",
                                       "email_address", "website_url", "area", "city", "state", "pin_code"])
    st.dataframe(updated_df.T)