--
-- PostgreSQL database dump
--

\restrict NIMUNOkaPtdCdjObyJbaf0P7t6ajNd6eleQC8Kb6eW6LZD4sz498aVIz0yn1kq9

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

-- Started on 2026-03-02 19:06:23

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 856 (class 1247 OID 16771)
-- Name: rol_usuario; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.rol_usuario AS ENUM (
    'Admin',
    'Profesor',
    'Alumno',
    'Oficina'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 220 (class 1259 OID 16740)
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id_user integer NOT NULL,
    user_name character varying(50) NOT NULL,
    password text NOT NULL,
    user_mail character varying(100) CONSTRAINT users_user_email_not_null NOT NULL,
    creado_en timestamp with time zone NOT NULL,
    actualizado_en timestamp with time zone NOT NULL,
    rol public.rol_usuario NOT NULL
);


--
-- TOC entry 219 (class 1259 OID 16739)
-- Name: users_id_user_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_user_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5018 (class 0 OID 0)
-- Dependencies: 219
-- Name: users_id_user_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_user_seq OWNED BY public.users.id_user;


--
-- TOC entry 4859 (class 2604 OID 16743)
-- Name: users id_user; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id_user SET DEFAULT nextval('public.users_id_user_seq'::regclass);


--
-- TOC entry 4861 (class 2606 OID 16768)
-- Name: users unique_user_email; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT unique_user_email UNIQUE (user_mail);


--
-- TOC entry 4863 (class 2606 OID 16751)
-- Name: users unique_user_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT unique_user_name UNIQUE (user_name);


--
-- TOC entry 4865 (class 2606 OID 16749)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id_user);


-- Completed on 2026-03-02 19:06:23

--
-- PostgreSQL database dump complete
--

\unrestrict NIMUNOkaPtdCdjObyJbaf0P7t6ajNd6eleQC8Kb6eW6LZD4sz498aVIz0yn1kq9

-- -------------------------------------------------------------
-- Tabla de eventos personales/external prevista para calendario
-- -------------------------------------------------------------

-- cada fila puede pertenecer a un usuario (user_id) o ser un
-- evento "externo" (user_id NULL) que se inyectará posteriormente.
-- la columna "external" facilita distinguir los orígenes sin
-- romper la integridad referencial.

CREATE TABLE public.events (
    id_event serial PRIMARY KEY,
    user_id integer REFERENCES public.users(id_user) ON DELETE CASCADE,
    title character varying(200) NOT NULL,
    description text,
    start_date timestamp with time zone NOT NULL,
    end_date timestamp with time zone NOT NULL,
    creado_en timestamp with time zone NOT NULL DEFAULT NOW(),
    actualizado_en timestamp with time zone NOT NULL DEFAULT NOW(),
    external boolean NOT NULL DEFAULT FALSE,
    source character varying(100)  -- nombre del origen si es externo
);

-- índice por usuario para acelerar búsquedas
CREATE INDEX ON public.events(user_id);

-- fin de la extensión de esquema




CREATE TABLE anuncios (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL,
    mensaje TEXT NOT NULL,
    prioridad VARCHAR(20) NOT NULL,
    fecha_publicacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);