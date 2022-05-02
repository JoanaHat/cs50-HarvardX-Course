-- Keep a log of any SQL queries you execute as you solve the mystery.

SELECT * FROM crime_scene_reports WHERE year = 2020 AND month = 7 AND day = 28;
-- Crime scene report:
--      Theft took place at 10:15 AM at Chamberlin Street courthouse
--      3 witnesses

SELECT * FROM interviews WHERE year = 2020 AND month = 7 AND day = 28;
-- Ruth: Saw thief leaving courthouse parking lot within 10 minutes of theft
-- Eugene: Saw thief in the morning at an ATM on Fifer Street withdrawing money
-- Raymond: Saw thief make a one minute call(Assumption: within ten minutes of theft) where he mentioned:
--          Planning to take earliest fight tomorrow(July 29, 2020)
--          Thief asked person on the phone to purchase fight ticket


SELECT name FROM people JOIN bank_accounts ON id = person_id WHERE account_number IN 
(SELECT account_number FROM atm_transactions WHERE year = 2020 AND month = 7 AND day = 28 
AND atm_location ="Fifer Street" And transaction_type = "withdraw");
/*
Ernest
Russell
Roy
Bobby
Elizabeth
Danielle
Madison
Victoria
*/


SELECT destination_airport_id, full_name, hour, minute  FROM airports JOIN flights ON airports.id = destination_airport_id WHERE flights.id IN 
(SELECT id FROM flights WHERE year = 2020 AND month = 7 AND day = 29 AND hour BETWEEN 1 AND 12);
/*
destination_airport_id | full_name | hour | minute
11 | San Francisco International Airport | 12 | 15
4 | Heathrow Airport | 8 | 20
1 | O'Hare International Airport | 9 | 30
*/

SELECT passport_number, origin_airport_id, destination_airport_id from passengers JOIN flights ON flight_id = flights.id WHERE flights.id IN
(SELECT flights.id FROM airports JOIN flights ON airports.id = destination_airport_id WHERE flights.id IN
(SELECT id FROM flights WHERE year = 2020 AND month = 7 AND day = 29 AND hour BETWEEN 1 AND 12 AND destination_airport_id = 4));
/*
passport_number | origin_airport_id | destination_airport_id
7214083635 | 8 | 4
1695452385 | 8 | 4
5773159633 | 8 | 4
1540955065 | 8 | 4
8294398571 | 8 | 4
1988161715 | 8 | 4
9878712108 | 8 | 4
8496433585 | 8 | 4
*/


SELECT name, passport_number FROM people WHERE name IN ('Ernest', 'Russell', 'Roy', 'Bobby', 'Elizabeth', 'Danielle','Madison', 'Victoria') AND people.passport_number IN
(SELECT passport_number from passengers JOIN flights ON passengers.flight_id = flights.id WHERE flights.id IN
(SELECT flights.id FROM airports JOIN flights ON airports.id = destination_airport_id WHERE flights.id IN
(SELECT id FROM flights WHERE year = 2020 AND month = 7 AND day = 29 AND hour BETWEEN 1 AND 12 )));
/*
name | passport_number
Bobby | 9878712108
Madison | 1988161715
Danielle | 8496433585
Ernest | 5773159633
*/


SELECT name, phone_number FROM people WHERE name IN ('Bobby', 'Madison','Danielle','Ernest') AND phone_number IN
(SELECT caller FROM phone_calls WHERE year = 2020 AND month = 7 AND day = 28 AND duration BETWEEN 0 AND 60);
/*
name | phone_number
Bobby | (826) 555-1652
Madison | (286) 555-6063
Ernest | (367) 555-5533
*/

SELECT name FROM people WHERE license_plate IN (SELECT courthouse_security_logs.license_plate FROM courthouse_security_logs WHERE year = 2020 AND month = 7 AND day = 28 AND hour = 10 AND minute BETWEEN 15 AND 25 AND license_plate IN 
(SELECT people.license_plate FROM people WHERE name IN ('Bobby', 'Madison','Danielle','Ernest') AND phone_number IN
(SELECT caller FROM phone_calls WHERE year = 2020 AND month = 7 AND day = 28 AND duration BETWEEN 0 AND 60)));
/*
name
Ernest
*/

SELECT name, phone_number FROM people WHERE phone_number IN
(SELECT receiver FROM phone_calls WHERE year = 2020 AND month = 7 AND day = 28 AND duration BETWEEN 0 AND 60 AND caller = "(367) 555-5533");
/*
name | phone_number
Berthold | (375) 555-8161
*/

SELECT city FROM airports WHERE id IN
(SELECT destination_airport_id FROM flights JOIN passengers ON id = flight_id WHERE passport_number = 5773159633);
/*
city
London
*/