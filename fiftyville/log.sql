-- Keep a log of any SQL queries you execute as you solve the mystery.

-- check crime reports for day
select 'crimes reported on Humphrey Street 28.7.2023' as '';
select description from crime_scene_reports
where year = 2023 and month = 7 and day = 28 and street = 'Humphrey Street';

select 'interviews talking about the bakery' as '';
select name, transcript
from interviews
where year = 2023 and month = 7 and day = 28 and transcript like '%bakery%';

-- people who withdrew from the leggett street ATM day of
CREATE TABLE primary_pois AS
SELECT people.*
FROM people JOIN bank_accounts ON people.id=bank_accounts.person_id
WHERE account_number IN
(SELECT account_number FROM atm_transactions WHERE year = 2023 AND month = 7 AND day = 28 AND atm_location = 'Leggett Street' AND transaction_type = 'withdraw');

SELECT 'people who withdrew from the leggett street ATM day of' AS '';
SELECT * FROM primary_pois;

SELECT 'calls that occured the day of that lasted less than a minute' '';
SELECT *
FROM phone_calls 
WHERE year = 2023 AND month = 7 AND day = 28 AND duration < 60;

-- sift by calls that occured the day of that lasted less than a minute
CREATE TABLE new_pois AS
SELECT *
FROM primary_pois
WHERE phone_number IN
(SELECT caller
  FROM phone_calls 
  WHERE year = 2023 AND month = 7 AND day = 28 AND duration < 60);

DROP TABLE primary_pois;
CREATE TABLE primary_pois AS SELECT * FROM new_pois;
DROP TABLE new_pois;

SELECT 'reduce suspects by call logs' AS '';
SELECT * FROM primary_pois;

-- thief called the accomplice
CREATE TABLE secondary_pois AS
SELECT * FROM people
WHERE phone_number in
(SELECT receiver
  FROM phone_calls 
  WHERE year = 2023 AND month = 7 AND day = 28 AND duration < 60);

select 'secondary suspects' as '';
select * from secondary_pois;

SELECT 'exits from bakery within 10 mins of 10:15' AS '';
SELECT * FROM bakery_security_logs
WHERE year = 2023 AND month = 7 AND day = 28 AND hour = 10 AND minute >15 AND minute <26 AND activity = 'exit';

/* getaway vehiclenot necessarily primary poi's
*CREATE TABLE new_pois AS
*SELECT * FROM primary_pois
*WHERE license_plate IN
*(SELECT license_plate FROM bakery_security_logs
  *  WHERE year = 2023 AND month = 7 AND day = 28 AND hour = 10 AND minute >22 AND activity = 'exit');
*/

SELECT 'exits cross-referenced with primary pois' AS '';
CREATE TABLE new_pois AS
SELECT * FROM primary_pois WHERE license_plate IN
(SELECT license_plate FROM bakery_security_logs
  WHERE year = 2023 AND month = 7 AND day = 28
  AND hour = 10 AND minute > 15 AND minute <26
  AND activity = 'exit');

-- secondary pois not in exits

DROP TABLE primary_pois;
CREATE TABLE primary_pois AS SELECT * FROM new_pois;
DROP TABLE new_pois;

SELECT * FROM primary_pois;

SELECT 'possible accomplice list cross-referenced with refined primary pois' AS '';
CREATE TABLE new_pois AS
SELECT * FROM secondary_pois
WHERE phone_number in
(SELECT receiver
  FROM phone_calls 
  WHERE year = 2023 AND month = 7 AND day = 28 AND duration < 60
  AND caller IN
  (SELECT phone_number FROM primary_pois));

DROP TABLE secondary_pois;
CREATE TABLE secondary_pois AS SELECT * FROM new_pois;
DROP TABLE new_pois;

SELECT * FROM secondary_pois;

-- the thief planned to leave town the next flight out
select 'earliest flight out of Fiftyville the day after' as '';
select * from flights
where origin_airport_id in
(select id from airports
  where city = 'Fiftyville')
and year = 2023 and month = 7 and day = 29
order by hour, minute asc
limit 1;

select 'people who flew in that flight' as '';
select * from people
where passport_number in
(select passport_number from passengers
  where flight_id = 36);

select 'pois who flew in that flight' as '';
create table new_pois as
select * from primary_pois
where passport_number in
(select passport_number from passengers
  where flight_id in
  (select id from flights
    where origin_airport_id in
    (select id from airports
      where city = 'Fiftyville')
    and year = 2023 and month = 7 and day = 29
    order by hour, minute asc
    limit 1));

  drop table primary_pois;
  create table primary_pois as select * from new_pois;
  drop table new_pois;

  select * from primary_pois;

  /* the accomplice didn't fly with them
  select 'secondary pois who flew in one of those flights' as '';
  select * from secondary_pois
  where passport_number in
  (select passport_number from
    passengers inner join flights on passengers.flight_id=flights.id
    where origin_airport_id in
    (select id from airports
      where city = 'Fiftyville')
    and year = 2023 and month = 7 and day = 29
    order by hour, minute asc
    limit 5);
  */

  /* let's trust it's the earliest
  select 'flight the thief took' as '';
  select * from flights
  where id in
  (select flight_id from passengers
    where passport_number in
    (select passport_number from primary_pois));
  */

  select 'to:' as '';
  select full_name, city from airports
  where id in
  (select destination_airport_id from flights
    where id in
    (select flight_id from passengers
      where passport_number in
      (select passport_number from primary_pois)));

  select 'people the thief called the day of theft for less than a minute' as '';
  select * from secondary_pois
  where phone_number in
  (SELECT receiver
    FROM phone_calls 
    WHERE year = 2023 AND month = 7 AND day = 28 AND duration < 60 and caller in
    (select phone_number from primary_pois));

  DROP TABLE primary_pois;
  DROP TABLE secondary_pois;

