from splinter import Browser
from pprintpp import pprint
from time import sleep
with Browser() as browser:
    # Defining the stupid websites
    shirt = "http://www.supremenewyork.com/shop/accessories/supreme-hanes-tagless-tees-3-pack/white"
    url = "http://www.supremenewyork.com/shop/all"
    checkout = 'https://www.supremenewyork.com/checkout'
    
    # WHERE YOU ENTER YOUR DUMB INFO
    name  = 'Emma Lantz'
    email = 'lantz.emma@gmail.com'
    phone = '6035477955'
    addrs = '3 Meadowbrook Village, Apt 7'
    city  = 'West Lebanon' #born and raised, on the playground ....
    zipy  = '03784'

    cc_year = '2018'
    cc_month = '11'
    cc_number = '1234'
    that_code_thingy = '123'


    # to pick your card type remove the # that's in front of it
    cc_type = 'master'
    # cc_type = 'american_express'
    # cc_type = 'visa'

    browser.visit(url)

    print "Add stuff to your cart and hit Enter when you're ready."
    var = raw_input("\nWaiting on you sistah")

    print "Here we go!"
    browser.visit(checkout)
    
    # Filling out the info out the form.
    form = browser.find_by_tag("form")
    form.find_by_id("order_billing_name").fill(name)
    form.find_by_id("order_email").fill(email)
    form.find_by_id("order_tel").fill(phone)
    form.find_by_id("bo").fill(addrs)
    form.find_by_id("order_billing_zip").fill(zipy)
    # form.find_by_id("order_billing_city").fill(city)
    form.find_by_id("number_v").fill(that_code_thingy)
    form.find_by_id("onb").fill(cc_number)
    form.find_by_id("credit_card_type").select(cc_type)
    form.find_by_id("credit_card_month").select(cc_month)
    form.find_by_id("credit_card_year").select(cc_year)
    
    # This is here to test the info you've entered, it wont process
    browser.find_by_name("commit").click()
    var = raw_input("Alright Emma, fill your shopping cart and hit enter: ")
