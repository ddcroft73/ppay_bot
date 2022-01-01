#PPay Bot

import json, smtplib, ssl
from selenium import webdriver 

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
          
PAYLOAD = "./payload.json"

def start_bot(headless: bool=False) -> None:
    chrome_options = webdriver.ChromeOptions()     

    if headless: chrome_options.add_argument("--headless")
    # anit_ automatin, But noting gets them all. TO remain even more incognito use requests, urlip, urlib2, cookielib
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    srv=Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=srv, options=chrome_options) 
    # try to keep the webdriver from setting off automation alarms. Doesnt always work.
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd(
        'Network.setUserAgentOverride', {
         "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'
         })
    driver.refresh()        
    driver.get(data["start"])     

    return driver
    
# function attmepts to wait for each element passed in before acessing it, 
# adjust the times for some timeouts. Some my stil time out but compared to not using WebDriverWait()
# before sending or clicking it seems to work much better.
def wait_and_find(delay: int, doing: str,  by_element: str, wait_for: str, send_data: str=None) -> str:
    result: str=None 
    WebDriverWait(drv, delay).until(EC.presence_of_element_located((by_element, wait_for)))

    match doing:
        case "send":
            drv.find_element(by_element, wait_for).send_keys(send_data)
        case "click":
            drv.find_element(by_element, wait_for).click()
        case "query":
            result = drv.find_element(by_element, wait_for)
    return result      

#load the data to run the site into a dictinoary     
def get_userdata() -> dict:
    with open(PAYLOAD, "r") as infile:
        data = json.load(infile)
    return data


# searches user DB for my info and returns my link
def goto_mypage() -> str:
    name_xpath = '//*[@id="name"]'
    last_xpath = '//*[@id="last_name"]'
    submit_xpath = "/html/body/div/div/div/section/div[1]/div[2]/div/form/div[6]/div/button"
    
    # wait for the forms to load
    # fill in the data
    wait_and_find(3, 'send', By.XPATH, name_xpath, data['first'])
    wait_and_find(3, 'send', By.XPATH, last_xpath, data['last'])
    wait_and_find(3, 'click', By.XPATH, submit_xpath)
    wait_and_find(3, 'click', By.LINK_TEXT, data['my_link_text'])

# fill sin the relevent data and submits payment
def submit_amount() -> None:
    payment_link_xpath = '/html/body/div/div/div/section/p[1]/a'
    payment_amount_xpath = '//*[@id="paymentAmount"]'
    continue_butt_xpath = '//*[@id="frmPayment"]/div/div/fieldset/div/button[2]'    
    total_arrearge_xpath = '//*[@id="details"]/tbody/tr[6]/td'
    balance_owed_xpath = '//*[@id="details"]/tbody/tr[7]/td'
    
    wait_and_find(3, 'click', By.XPATH, payment_link_xpath)
    wait_and_find(10, 'send', By.XPATH, payment_amount_xpath, data['payment_amt'])
    el = wait_and_find(3, 'query', By.XPATH, total_arrearge_xpath)
    balance_rears = el.text
    el = wait_and_find(3, 'query', By.XPATH, balance_owed_xpath)
    balance_before_pay = el.text
    wait_and_find(3, 'click', By.XPATH, continue_butt_xpath)

def submit_user_info() -> None:
    address_xpath = '//*[@id="CustomerInfo_Address1"]'
    city_xpath = '//*[@id="CustomerInfo_City"]'
    state_xpath = '//*[@id="CustomerInfo_State"]'
    zip_xpath = '//*[@id="CustomerInfo_Zip"]'
    phone_xpath = '//*[@id="Phone"]'
    email_xpath = '//*[@id="Email"]'
    next_button_xpath = '//*[@id="bntNextCustomerInfo"]'
    
    wait_and_find(10, 'send', By.XPATH, address_xpath, data['address'])
    wait_and_find(10, 'send', By.XPATH, city_xpath, data['city'])
    wait_and_find(10, 'send', By.XPATH, zip_xpath, data['zip'])
    wait_and_find(10, 'send', By.XPATH, phone_xpath, data['phone'])
    wait_and_find(10, 'send', By.XPATH, email_xpath, data['email'])
    wait_and_find(10, 'send', By.XPATH, state_xpath, data['state'])
    wait_and_find(10, 'click', By.XPATH, next_button_xpath)   

def submit_payment() -> None:
    card_num_xpath = '//*[@id="CCCardNumber"]'
    card_exp_month_xpath = '//*[@id="CCExpirationMonth"]'
    card_exp_year_xpath = '//*[@id="CCExpirationYear"]'
    card_csv_xpath = '//*[@id="CCCardCVV"]'
    name_xpath = '//*[@id="CCNameOnCard"]'
    next_xpath = '//*[@id="bntNextPaymentInfo"]'
    submit_xpath = '//*[@id="submitPayment"]'

    wait_and_find(10, 'send', By.XPATH, card_num_xpath, data['card_num'])
    wait_and_find(10, 'send', By.XPATH, card_exp_month_xpath, data['card_exp_month'])
    wait_and_find(10, 'send', By.XPATH, card_exp_year_xpath, data['card_exp_year'])
    wait_and_find(10, 'send', By.XPATH, card_csv_xpath, data['csv'])
    wait_and_find(10, 'send', By.XPATH, name_xpath, data['first'] + " " + data['last'])
    wait_and_find(10, 'click', By.XPATH, next_xpath)      
#    wait_and_find(6, 'click', By.XPATH, submit_xpath)      


# TODO:
# formats a nice message froom the dict gatered from the last page
def format_details(before: str, rears: str, after: str) -> str:
    print(f"{before} is owed before pay.\n{after} is owed after the payment.\n{rears} is what you're behind.")
    return

def send_email(msg: str) -> None:    
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

#END TODO:


if __name__ == '__main__':

    balance_before_pay = ""
    balance_after_pay = ""
    balance_rears = ""      

    # start the webdriver and load the payload data
    data = get_userdata()
    drv = start_bot(headless=False)

    # call individual functions to take care of each page
    goto_mypage()     
    submit_amount()   
    submit_user_info()
    submit_payment()

#    print(balance_before_pay, balance_rears)
#    drv.close()  # SHutdown the webdriver

   # message = format_details(balance_before_pay, balance_rears, balance_after_pay)
   # send email of payment info
   # send_email(data, message)

    
