#PPay Bot

import json, smtplib, ssl
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
          

DRIVER_LOC = "C:\\Program Files\\Google\\Chrome\\Application\\96.0.4664.110\\chromedriver.exe"
PAYLOAD = "./payload.json"


balance_before_pay = ""
balance_after_pay = ""
balance_rears = ""

def start_bot(data: dict, option: str="") -> None:
    # decide if headless or normal
    if option == "--headless":
        chrome_options = Options()
        chrome_options.add_argument(option)
        driver = webdriver.Chrome(executable_path=DRIVER_LOC, options=chrome_options)  
    else:        
        driver = webdriver.Chrome(executable_path=DRIVER_LOC)  
        driver.maximize_window()
        driver.refresh()       

    driver.get(data["start"])       
    return driver
    
def shutdown(driver: object) -> None:
    driver.close()

def wait(d:webdriver ,delay: int, by_element: str, wait_for) -> None:
    WebDriverWait(d, delay).until(EC.presence_of_element_located((by_element, wait_for)))    
     
def get_userdata() -> dict:
    with open(PAYLOAD, "r") as infile:
        data = json.load(infile)
    return data

# searches user DB for my info and returns my link
def goto_mypage(d, data: dict) -> str:
    name_xpath = '//*[@id="name"]'
    last_xpath = '//*[@id="last_name"]'
    submit_xpath = "/html/body/div/div/div/section/div[1]/div[2]/div/form/div[6]/div/button"
    
    # wait for the forms to load
    # fill in the data
    d.find_element(By.XPATH, name_xpath).send_keys(data['first'])
    d.find_element(By.XPATH, last_xpath).send_keys(data['last'])
    d.find_element(By.XPATH, submit_xpath).click()    
    # wait for page to load
    wait(d, 8, By.LINK_TEXT, data['my_link_text'])
    # load submit payment page
    d.find_element(By.LINK_TEXT, data['my_link_text']).click()



# fill sin the relevent data and submits payment
def submit_amount(d, user_data: dict) -> tuple:
    payment_link_xpath = '/html/body/div/div/div/section/p[1]/a'
    payment_amount_xpath = '//*[@id="paymentAmount"]'
    continue_butt_xpath = '//*[@id="frmPayment"]/div/div/fieldset/div/button[2]'    
    total_arrearge_xpath = '//*[@id="details"]/tbody/tr[6]/td'
    balance_owed_xpath = '//*[@id="details"]/tbody/tr[7]/td'
    
    #navigate to the personal info page
    d.find_element(By.XPATH, payment_link_xpath).click() 
     # wait for page to load, make sure the payment button is there.
    wait(d, 8, By.XPATH, continue_butt_xpath)
    d.find_element(By.XPATH, payment_amount_xpath).send_keys(user_data['payment_amt'])

    # get data about balances
    el = d.find_element(By.XPATH, total_arrearge_xpath)
    rears = el.text
    el = d.find_element(By.XPATH, balance_owed_xpath)
    before_pay = el.text

    d.find_element(By.XPATH, continue_butt_xpath).click() 
    return rears, before_pay

def submit_user_info(d, data: dict) -> None:
    #name_xpath = '//*[@id="CustomerInfo_FirstName"]'
    #last_xpath = '//*[@id="CustomerInfo_LastName"]'
    address_xpath = '//*[@id="CustomerInfo_Address1"]'
    city_xpath = '//*[@id="CustomerInfo_City"]'
    state_xpath = '//*[@id="CustomerInfo_State"]'
    zip_xpath = '//*[@id="CustomerInfo_Zip"]'
    phone_xpath = '//*[@id="Phone"]'
    email_xpath = '//*[@id="Email"]'
    
    next_button_xpath = '//*[@id="bntNextCustomerInfo"]'
    # wait for entore page to load. focus on the "next" button
    wait(d, 6, By.XPATH, next_button_xpath)
    #fill in user info
    d.find_element(By.XPATH, address_xpath).send_keys(data['address'])
    d.find_element(By.XPATH, city_xpath).send_keys(data['city'])
    d.find_element(By.XPATH, zip_xpath).send_keys(data['zip'])
    d.find_element(By.XPATH, phone_xpath).send_keys(data['phone'])
    d.find_element(By.XPATH, email_xpath).send_keys(data['email'])
    d.find_element(By.XPATH, state_xpath).send_keys('SC')      
    d.find_element(By.XPATH, next_button_xpath).click() 

def submit_payment(d, data) -> None:
    card_num_xpath = '//*[@id="CCCardNumber"]'
    card_exp_month_xpath = '//*[@id="CCExpirationMonth"]'
    card_exp_year_xpath = '//*[@id="CCExpirationYear"]'
    card_csv_xpath = '//*[@id="CCCardCVV"]'
    name_xpath = '//*[@id="CCNameOnCard"]'
    next_xpath = '//*[@id="bntNextPaymentInfo"]'
    submit_xpath = '//*[@id="submitPayment"]'

    #wait fot page to load
    wait(d, 6, By.XPATH, next_xpath)
    d.find_element(By.XPATH, card_num_xpath).send_keys(data['card_num'])
    d.find_element(By.XPATH, card_exp_month_xpath).send_keys(data['card_exp_month'])
    d.find_element(By.XPATH, card_exp_year_xpath).send_keys(data['card_exp_year'])
    d.find_element(By.XPATH, card_csv_xpath).send_keys(data['csv'])
    d.find_element(By.XPATH, name_xpath).send_keys(data['first'] + " " + data['last'])      
    d.find_element(By.XPATH, next_xpath).click()     
    # just to make sure the button is there
    wait(d, 6, By.XPATH, submit_xpath)
    d.find_element(By.XPATH, submit_xpath).click() 



# formats a nice message froom the dict gatered from the last page
def format_details(before: str, rears: str, after: str) -> str:
    print(f"{before} is owed before pay.\n{after} is owed after the payment.\n{rears} is what you're behind.")
    return


def send_email(data: dict, msg: str) -> None:    
    port = 587  # For starttls
    smtp_server = "smtp.gmail.com"
    sender_email = data['out_email']
    receiver_email = data['in_email']
    password = data['email_pword']
    
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls(context=context)
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg)

if __name__ == '__main__':

    data = get_userdata()
    drv = start_bot(data)
    goto_mypage(drv, data)     
    submit_amount(drv, data)   

    submit_user_info(drv, data)
    submit_payment(drv, data)
    shutdown(drv)  # SHutdown the webdriver

   # message = format_details(balance_before_pay, balance_rears, balance_after_pay)
   # send email of payment info
   # send_email(data, message)

    
