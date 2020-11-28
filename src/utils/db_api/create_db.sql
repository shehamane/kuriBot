create table users
(
    chat_id bigint not null constraint users_pk primary key,
    username text,
    full_name text,
    id serial not null
);

alter table users
    owner to postgres;

create unique index users_id_uindex
    on users (id);