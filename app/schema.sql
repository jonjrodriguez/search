drop table if exists users;
create table users (
  id integer primary key autoincrement,
  username text not null,
  password text not null,
  is_admin boolean not null
);

drop table if exists crawls;
create table crawls (
  id integer primary key autoincrement,
  filepath text not null,
  crawl_date datetime not null
);

drop table if exists outlinks;
create table outlinks (
  id integer primary key autoincrement,
  url string not null,
  outlink text not null
);

drop table if exists duplicates;
create table duplicates (
  id integer primary key autoincrement,
  url text not null,
  duplicate text not null,
  similarity float not null
);