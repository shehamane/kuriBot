create table if not exists users
(
    chat_id   bigint not null
        constraint users_pk primary key,
    username  text,
    full_name text,
    id        serial not null
);

alter table users
    owner to postgres;

create unique index if not exists users_id_uindex
    on users (id);

-----------------------------------------

create table if not exists categories
(
    id        serial  not null
        constraint categories_pk primary key,
    name      text    not null,
    parent_id int,
    is_parent boolean not null
);

alter table categories
    owner to postgres;

create unique index if not exists categories_id_uindex
    on categories (id);

insert into categories (id, name, parent_id, is_parent)
values (1, 'MAIN', null, true);

----------------------------------------------------------

create table if not exists products
(
    id          serial not null
        constraint products_pk primary key,
    name        text,
    category_id int    not null
        REFERENCES categories (id),
    description text,
    price       int    not null
);

alter table products
    owner to postgres;

create unique index if not exists products_id_uindex
    on products (id);


---------------------------------------------------


create table if not exists cart
(
    id         serial not null
        constraint cart_pk primary key,
    user_id    int    not null
        REFERENCES users (id),
    product_id int    not null
        REFERENCES products (id),
    amount     int    not null
);

alter table cart
    owner to postgres;

create unique index if not exists cart_id_uindex
    on cart (id);


-------------------------------------------------

create view categories_info
    (id, name, parent_id, is_parent, products_number)
as
select cat.id, cat.name, cat.parent_id, cat.is_parent, count(p.*)
from categories cat
         left join products p on p.category_id = cat.id
where cat.is_parent = false
group by cat.name, cat.id, cat.parent_id, cat.is_parent;


