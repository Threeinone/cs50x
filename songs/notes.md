# Case

The CS50 duck was stolen on *july 28, 2023* at *Humphrey Street*.
we need to identify the thief, their wherabouts, and any accomplices

# Clues

## crime_scene_reports

- the theft happened at 10:15am
- at *Humphrey Street Bakery*
- 3 witnessed interviewed the same day, all mention the bakery

## interviews

- Ruth testifies 10 minutes after the theft (10:25) she witnessed the thief get in a car and drive off
    - possibly picked up by parking lot surveilance
- Eugene saw the thief earlier that morning on *Legget Street* withdrawing money from the ATM
- Raymond overheard the thief talking on the phone with an accomplice for < a min. They were planning to take the earliest flight out of fiftyville the next day (29.7.2023)
    - the accomplice was the one going to buy the ticket

## bakery_security_logs

exits from bakery occuring near 10:25:
id|year|month|day|hour|minute|activity|license_plate
266|2023|7|28|10|23|exit|322W7JE
267|2023|7|28|10|23|exit|0NTHK55
268|2023|7|28|10|35|exit|1106N58

## people

hits from querying license plates from bakery_security_logs:
id|name|phone_number|passport_number|license_plate
449774|Taylor|(286) 555-6063|1988161715|1106N58
514354|Diana|(770) 555-1861|3592750733|322W7JE
560886|Kelsey|(499) 555-9472|8294398571|0NTHK55

## atm_transactions

withdrawals from leggett street the day of the theft:
id|account_number|year|month|day|atm_location|transaction_type|amount
246|28500762|2023|7|28|Leggett Street|withdraw|48
264|28296815|2023|7|28|Leggett Street|withdraw|20
266|76054385|2023|7|28|Leggett Street|withdraw|60
267|49610011|2023|7|28|Leggett Street|withdraw|50
269|16153065|2023|7|28|Leggett Street|withdraw|80
288|25506511|2023|7|28|Leggett Street|withdraw|20
313|81061156|2023|7|28|Leggett Street|withdraw|30
336|26013199|2023|7|28|Leggett Street|withdraw|35

## bank_accounts

people who withdrew funds on leggett street the day of
name|account_number
Bruce|49610011
Diana|26013199
Brooke|16153065
Kenny|28296815
Iman|25506511
Luca|28500762
Taylor|76054385
Benista|81061156


## flights inner join airports on flights.origin_airport_id=airports.id

earliest flight of the day after theft:
id|origin_airport_id|destination_airport_id|year|month|day|hour|minute|id|abbreviation|full_name|city
36|8|4|2023|7|29|8|20|8|CSF|Fiftyville Regional Airport|Fiftyville

destination airport 4 is:
id|abbreviation|full_name|city
4|LGA|LaGuardia Airport|New York City

## callers or receivers of calls the day of the crime who called less than a minute and license plates showed up on bakery security footage after 10:20 the day of

id|name|phone_number|passport_number|license_plate
395717|Kenny|(826) 555-1652|9878712108|30G67EN
398010|Sofia|(130) 555-0289|1695452385|G412CB7
438727|Benista|(338) 555-6650|9586786673|8X428L0
449774|Taylor|(286) 555-6063|1988161715|1106N58
514354|Diana|(770) 555-1861|3592750733|322W7JE
560886|Kelsey|(499) 555-9472|8294398571|0NTHK55
686048|Bruce|(367) 555-5533|5773159633|94KL13X
907148|Carina|(031) 555-6622|9628244268|Q12B3Z3

# Persons of interest
Diana, Kelsey, and Taylor's names all keep popping up
diana and taylor both withdrew funds from ATM

# Timeline

1. thief withdraws money. witnessed early in the morning by Eugene
2. thief arrives at humphrey street bakery, makes a phone call to accomplice about plans to leave the city first flight next morning. Accomplice is to purchase tickets. call lasts less than a minute. witnessed by Raymond
3. 10:15, the duck is stolen
4. approx. 10 minutes later, thief gets in a car and drives off. Bakery parking surveilance records the exit. witnessed by Ruth
5. the following morning at 8:20 a plane is scheduled to go from fiftyville regional airport to LaGuardia airport in New York

# line of logic

atm_transactions will have recorded thief withdrawal from atm day of theft
    can be traced to PoIs via bank_accounts
phone_calls metadata will show calls the day of theft that lasted less than a minute
    caller can be linked to PoI phone number
    receivers are new secondary PoIs
bakery_security_logs will show cars leaving bakery at approximately 10:25
    either linked to first or second PoIs
flights out of fiftyville combined with passengers to get passport numbers
    %%should check more than earliest flight for thoroughness (what if **earliest** flight already booked?)%%
    both primary and secondary PoI will be linkable to flight
