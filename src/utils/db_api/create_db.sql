-- create table users
-- (
--     chat_id   bigint not null
--         constraint users_pk primary key,
--     username  text,
--     full_name text,
--     id        serial not null
-- );
--
-- alter table users
--     owner to postgres;
--
-- create unique index users_id_uindex
--     on users (id);
--
-- create table products
-- (
--     id          serial not null
--         constraint products_pk primary key,
--     name        text,
--     description text
-- );
--
-- alter table products
--     owner to postgres;
--
-- create unique index products_id_uindex
--     on products (id);
--
--
create table cart
(
    id         serial not null
        constraint cart_pk primary key,
    user_id    int    not null
        REFERENCES users (id),
    product_id int    not null
        REFERENCES products (id),
    number     int    not null
);

alter table cart
    owner to postgres;

create unique index cart_id_uindex
    on products (id);