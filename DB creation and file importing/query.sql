#Creating database lms(Library Management System)

create database lms; 
use lms;

#Creating the tables according to the schema

create table book( isbn varchar(10) primary key, title varchar(1000));
create table authors( author_id serial primary key, name varchar(1000));

create table book_authors( author_id int, isbn varchar(10), foreign key(author_id) references authors(author_id), foreign key(isbn) references book(isbn));
create table borrower (card_id serial primary key, ssn varchar(20), bname varchar(100), address varchar(250), phone varchar(30));

create table book_loans( loan_id serial primary key, isbn varchar(10) references book(isbn), card_id int references borrower(card_id), date_out date, due_date date, date_in date);   
create table fines( loan_id int references book_loans(loan_id), fine_amt decimal, Paid Boolean);

#Creating temporary tables to insert values into the main tables

create table authors_temp(name varchar(100));
insert into authors (name) Select distinct name from authors_temp;

create table book_authors_temp(isbn varchar(10), name varchar(100));
insert into book_authors (author_id,isbn) Select author_id,isbn from authors,book_authors_temp where authors.name=book_authors_temp.name;

#All the data from the .csv files was sorted and imported into the respective tables using the import wizard tool available in postgres