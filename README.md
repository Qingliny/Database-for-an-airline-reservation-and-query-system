# Database-for-an-airline-reservation-and-query-system
In this project, we are going to build a database for an airline reservation and query system. Customers can find ticket information like price, departure date, seat number, etc. for a specific flight and can also retrieve history ticket orders in this database. 
In this project, we are going to build a database for an airline reservation and query system. Customers can find ticket information like price, departure date, seat number, etc. for a specific flight and can also retrieve history ticket orders in this database. According to the requirements for this airline reservation system, we design an ER diagram as follows:

The entity set includes Order, Customer, Tickets, (Economy, Business, First Class), Airplane, Airlines, Flight, Airport, and the relationship set includes Booked, Inquiry, Owned by, Reservation, Departure, Arrival.

The data source we are going to use is: 1. Real time info about flights from the external API; 2. History orders for flights from relevant official websites; 3. Fabricated data like customers info;

The SQL schema for this design is as follows:
Customer (cid, cname, phone_no, passport_no, email)
Order (reserve_no, status, time, delay)
Tickets (ticket_no, seat_num)
Flight (flightid, fare, date, schedule)
Airport (apid, apname, country, city)
Airplane (register_no, model, seat_num)
Airline (alcode, alname) 

Booked (reserve_no, cid, FK(reserve_no) -> Order, FK(cid) -> Customer)
OwnedBy (register_no, alcode, FK(register_no) -> Airplane, FK(alcode) -> Airline)
AssignedTo (flightid, register_no, alcode, 
                     FK(flightid) -> Flight, 
                     FK(register_no) -> Airplane, 
                     FK(alcode) -> Airline)
Arrival (flightid, apid, atime, FK(flightid) -> Flight, FK(apid) -> Airport)
Departure (flightid, apid, dtime, FK(flightid) -> Flight, FK(apid) -> Airport)
Reservation (cid, ticket_no, flightid, seat_no
                     FK(cid) -> Customer, 
                     FK(ticket_no) -> Tickets,
                     FK(flightid) -> Flight)
Inquiry (cid, ticket_no, from, to
              FK(cid) -> Customer, 
              FK(ticket_no) -> Tickets)



