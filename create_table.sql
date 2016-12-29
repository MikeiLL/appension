-- Table names are flush left, and column definitions are
-- indented by at least one space or tab. Blank lines and
-- lines beginning with a double hyphen are comments.

tracks
	id serial primary key
	artist varchar not null default ''
	title varchar not null default ''
	filename varchar not null default ''
	artwork bytea not null default ''
	length double precision not null default 0
	xfade int not null default 0
	itrim int not null default 0
	otrim int not null default 0
	lyrics text not null default ''
	story text not null default ''
	status smallint not null default 0
	submitted timestamptz not null default now()
	submitter varchar not null default ''
	submitteremail varchar not null default ''
	comments varchar not null default ''
	enqueued int not null default 0
	played int not null default 0
	sequence int not null default 0
	keywords varchar not null default ''
	url varchar not null default ''
	analysis varchar not null default ''
	userid int not null default 0

users
	id serial primary key
	username varchar not null unique
	email varchar not null unique
	password varchar not null default ''
	user_level int not null default 1 -- banned=0, user=1, admin=2
	status int not null default 0
	hex_key varchar not null default ''

outreach
	id serial primary key
	message varchar not null default ''
	created timestamptz not null default now()
	processed int not null default 0
