drop table if exists user;
create table user (
  id integer primary key autoincrement,
  username text not null,
  email text not null,
  password text not null
);

drop table if exists documents;
create table documents (
  id integer primary key autoincrement,
  doc_id integer not null,
  url text not null
);

drop table if exists outlinks;
create table outlinks (
  id integer primary key autoincrement,
  document_id integer not null,
  outlink_id integer not null
);

drop table if exists inlinks;
create table inlinks (
  id integer primary key autoincrement,
  document_id integer not null,
  inlink_id integer not null
);