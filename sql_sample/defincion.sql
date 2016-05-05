BEGIN TRANSACTION;
CREATE TABLE "votos_v" (
	`region`	TEXT,
	`provincia`	TEXT,
	`municipio`	TEXT,
	`partido`	TEXT,
	`votes_presential`	INT,
	`votes_percent`	NUM,
	`seats`	INT,
	`ord`	INT,
	`fakedate`	INTEGER,
	FOREIGN KEY(partido) REFERENCES partidos(code),
	FOREIGN KEY(municipio) REFERENCES localidades(municipio)
);
CREATE TABLE votos_provincia(
  region TEXT,
  provincia TEXT,
  partido TEXT,
  votes_presential INT,
  votes_percent NUM,
  seats INT,
  ord INT
);
CREATE TABLE "votos_locales" (
	`region`	TEXT,
	`provincia`	TEXT,
	`municipio`	TEXT,
	`partido`	TEXT,
	`votes_presential`	INT,
	`votes_percent`	NUM,
	`seats`	INT,
	`ord`	INT,
	`fakedate`	INTEGER
);
CREATE TABLE partidos(code TEXT,acronym TEXT,name TEXT);
CREATE TABLE localidades(
  region TEXT,
  provincia TEXT,
  municipio TEXT,
  isla TEXT,
  nombre TEXT
);
CREATE TABLE `geo_rel` (
	`tipo_padre`	TEXT,
	`tipo_hijo`	TEXT,
	`padre`	TEXT,
	`hijo`	TEXT
);
CREATE TABLE "geo" (
	`codigo`	TEXT,
	`tipo`	TEXT,
	`nombre`	TEXT
);
COMMIT;
