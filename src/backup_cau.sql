--
-- PostgreSQL database dump
--

\restrict wydkqiIDM6LWcGy1EK244LtEysAlfQdUSSwoS9vdjfXdYYshgdYDmUuAbBk9CMt

-- Dumped from database version 18.0 (Debian 18.0-1.pgdg13+3)
-- Dumped by pg_dump version 18.0 (Debian 18.0-1.pgdg13+3)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.categories (
    id integer NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE public.categories OWNER TO postgres;

--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categories_id_seq OWNER TO postgres;

--
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.categories_id_seq OWNED BY public.categories.id;


--
-- Name: departments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.departments (
    id integer NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE public.departments OWNER TO postgres;

--
-- Name: departments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.departments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.departments_id_seq OWNER TO postgres;

--
-- Name: departments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.departments_id_seq OWNED BY public.departments.id;


--
-- Name: interactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.interactions (
    id integer NOT NULL,
    user_id integer,
    category_id integer,
    input_text text NOT NULL,
    response_text text NOT NULL,
    sentiment_id integer,
    urgency_id integer,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.interactions OWNER TO postgres;

--
-- Name: interactions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.interactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.interactions_id_seq OWNER TO postgres;

--
-- Name: interactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.interactions_id_seq OWNED BY public.interactions.id;


--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_id_seq OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: sentiments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sentiments (
    id integer NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE public.sentiments OWNER TO postgres;

--
-- Name: sentiments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sentiments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sentiments_id_seq OWNER TO postgres;

--
-- Name: sentiments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sentiments_id_seq OWNED BY public.sentiments.id;


--
-- Name: urgencies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.urgencies (
    id integer NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE public.urgencies OWNER TO postgres;

--
-- Name: urgencies_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.urgencies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.urgencies_id_seq OWNER TO postgres;

--
-- Name: urgencies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.urgencies_id_seq OWNED BY public.urgencies.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(100) NOT NULL,
    role_id integer,
    department_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);


--
-- Name: departments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departments ALTER COLUMN id SET DEFAULT nextval('public.departments_id_seq'::regclass);


--
-- Name: interactions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interactions ALTER COLUMN id SET DEFAULT nextval('public.interactions_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: sentiments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sentiments ALTER COLUMN id SET DEFAULT nextval('public.sentiments_id_seq'::regclass);


--
-- Name: urgencies id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.urgencies ALTER COLUMN id SET DEFAULT nextval('public.urgencies_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.categories (id, name) FROM stdin;
1	Error Software
2	Normativa ISO/ANSI
3	Modelado 3D
4	Planos 2D
5	Licencias
\.


--
-- Data for Name: departments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.departments (id, name) FROM stdin;
1	Diseño (CAD)
2	Simulación (CAE)
3	Prototipos
4	IT / Soporte
\.


--
-- Data for Name: interactions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.interactions (id, user_id, category_id, input_text, response_text, sentiment_id, urgency_id, "timestamp") FROM stdin;
1	1	3	Como puedo hacer un hole en Catia	Para crear un agujero en Catia, puedes utilizar la herramienta 'Hole' en el menú 'Insertar' o presionar el atajo 'Ctrl + H'. Selecciona el tipo de agujero deseado y ajusta las dimensiones según sea necesario.	2	1	2026-01-10 11:23:46.576228
2	1	5	No tengo licencia activa de catia y es muy urgente porque necesito trabajar	Puedes contactar con el departamento de licencias para obtener una licencia temporal o activar la tuya. Si no tienes acceso a la plataforma, puedes intentar acceder a través de un navegador diferente o contactar con el soporte técnico de Dassault Systèmes.	3	3	2026-01-10 14:38:44.131304
3	1	5	como me pongo en contacto con el departamento de licencias	Puedes contactar con el departamento de licencias a través del correo electrónico [licencias@cun.edu.uy](mailto:licencias@cun.edu.uy) o llamando al teléfono 2906-8000.	2	1	2026-01-10 14:39:29.901002
4	1	1	y para tomar un cafe?	Disculpa, solo estoy capacitado para resolver dudas de ingeniería y software CAD.	2	1	2026-01-10 14:40:08.793302
5	1	4	Como creo un plano en Catia	Para crear un plano en Catia, selecciona la herramienta 'Plano' en el menú de herramientas o presiona el atajo de teclado 'Ctrl + Shift + P'. Luego, selecciona el punto de referencia y el tamaño del plano según tus necesidades.	2	1	2026-01-10 18:01:42.920107
6	3	3	Como pongo un tornillo en Catia	Para insertar un tornillo en Catia, selecciona el componente 'Tornillo' en la biblioteca de piezas estándar o crea uno personalizado. Luego, arrastra y suelta el tornillo en el modelo 3D. Puedes ajustar la posición y la orientación del tornillo utilizando las herramientas de manipulación.	2	1	2026-01-12 13:01:04.687804
7	13	1	Hazme el proyecto de Ingenieria 	Error técnico en el servicio de IA.	2	3	2026-01-12 13:03:03.167082
8	13	1	Dime como quedo ayer el Madrid	Error técnico en el servicio de IA.	2	3	2026-01-12 13:03:20.663798
9	7	5	Necesito cambiar una licencia de Catia y no se donde encontrarla	La licencia de Catia se encuentra en el menú 'Herramientas' > 'Opciones de sistema' > 'Licencias'. También puedes buscar en el menú 'Ayuda' > 'Sobre Catia' para obtener información sobre la licencia actual.	2	1	2026-01-12 14:41:28.796374
10	1	1	como hago un sketch de un cuadrado	Lo siento, hubo un error procesando tu solicitud o perdiendo el contexto.	2	2	2026-01-13 09:13:34.221378
11	1	3	como hago un sketch	Para hacer un sketch en software de diseño asistido por computadora (CAD) como CATIA, SolidWorks o AutoCAD, generalmente sigues estos pasos: 1) Abre el software y crea un nuevo documento o proyecto. 2) Selecciona la herramienta de sketch o dibujo. 3) Establece las unidades y la escala de trabajo. 4) Utiliza las herramientas de dibujo como líneas, arcos, curvas y polígonos para crear tu sketch. 5) Asegúrate de utilizar las restricciones y relaciones para mantener la precisión y la integridad geométrica de tu diseño. 6) Una vez que hayas completado tu sketch, puedes extruirlo o utilizarlo como base para crear un modelo 3D.	1	2	2026-01-13 09:20:19.158498
12	1	3	y despues un pad?	Después de crear un sketch, puedes utilizar la herramienta 'Pad' o 'Extrusión' para convertir tu sketch 2D en un sólido 3D. Para hacer un pad, generalmente sigues estos pasos: 1) Selecciona el sketch que deseas extruir. 2) Selecciona la herramienta 'Pad' o 'Extrusión' en el menú de herramientas. 3) Establece la distancia o la altura de la extrusión. 4) Puedes elegir si la extrusión es hacia arriba, hacia abajo o en ambos sentidos. 5) Ajusta cualquier otra opción de configuración según sea necesario, como la dirección de la extrusión o la creación de un cuerpo sólido. 6) Confirma la operación para crear el pad. Ahora tienes un sólido 3D basado en tu sketch original.	1	2	2026-01-13 09:20:37.596092
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id, name) FROM stdin;
1	Admin
2	User
3	Manager
\.


--
-- Data for Name: sentiments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sentiments (id, name) FROM stdin;
1	Positivo
2	Neutro
3	Negativo
4	Enfadado/Frustrado
\.


--
-- Data for Name: urgencies; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.urgencies (id, name) FROM stdin;
1	Baja
2	Media
3	Alta
4	Crítica
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, email, role_id, department_id, created_at) FROM stdin;
1	Sergio	sergio@cau.com	1	1	2026-01-10 11:22:57.226892
3	Alvaro	alvaro@empresa.com	3	3	2026-01-10 15:47:24.246981
4	Andrea	andrea@empresa.com	3	3	2026-01-10 15:47:24.246981
5	Diego	diego@empresa.com	3	3	2026-01-10 15:47:24.246981
6	Noha	noha@empresa.com	3	3	2026-01-10 15:47:24.246981
7	David	david@empresa.com	3	4	2026-01-10 15:47:24.246981
8	Irina	irina@empresa.com	3	4	2026-01-10 15:47:24.246981
9	Matilde	matilde@empresa.com	3	4	2026-01-10 15:47:24.246981
10	Estibaliz	estibaliz@empresa.com	2	4	2026-01-10 15:47:24.246981
11	Itxaso	itxaso@empresa.com	3	4	2026-01-10 15:47:24.246981
12	Rebeca	rebeca@empresa.com	3	2	2026-01-10 15:47:24.246981
13	Mikel	mikel@empresa.com	2	2	2026-01-10 15:47:24.246981
14	Ane	ane@empresa.com	2	4	2026-01-10 15:47:24.246981
15	Zigor	zigor@empresa.com	2	1	2026-01-10 15:47:24.246981
16	Iker	iker@empresa.com	3	4	2026-01-10 15:47:24.246981
17	Mafalda	mafalda@empresa.com	3	1	2026-01-10 15:47:24.246981
18	Miguel	miguel@empresa.com	2	1	2026-01-10 15:47:24.246981
\.


--
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.categories_id_seq', 5, true);


--
-- Name: departments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.departments_id_seq', 4, true);


--
-- Name: interactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.interactions_id_seq', 12, true);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_seq', 3, true);


--
-- Name: sentiments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sentiments_id_seq', 4, true);


--
-- Name: urgencies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.urgencies_id_seq', 4, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 18, true);


--
-- Name: categories categories_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_name_key UNIQUE (name);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: departments departments_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_name_key UNIQUE (name);


--
-- Name: departments departments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_pkey PRIMARY KEY (id);


--
-- Name: interactions interactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interactions
    ADD CONSTRAINT interactions_pkey PRIMARY KEY (id);


--
-- Name: roles roles_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_name_key UNIQUE (name);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: sentiments sentiments_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sentiments
    ADD CONSTRAINT sentiments_name_key UNIQUE (name);


--
-- Name: sentiments sentiments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sentiments
    ADD CONSTRAINT sentiments_pkey PRIMARY KEY (id);


--
-- Name: urgencies urgencies_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.urgencies
    ADD CONSTRAINT urgencies_name_key UNIQUE (name);


--
-- Name: urgencies urgencies_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.urgencies
    ADD CONSTRAINT urgencies_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: interactions interactions_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interactions
    ADD CONSTRAINT interactions_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id);


--
-- Name: interactions interactions_sentiment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interactions
    ADD CONSTRAINT interactions_sentiment_id_fkey FOREIGN KEY (sentiment_id) REFERENCES public.sentiments(id);


--
-- Name: interactions interactions_urgency_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interactions
    ADD CONSTRAINT interactions_urgency_id_fkey FOREIGN KEY (urgency_id) REFERENCES public.urgencies(id);


--
-- Name: interactions interactions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interactions
    ADD CONSTRAINT interactions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: users users_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.departments(id);


--
-- Name: users users_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);


--
-- PostgreSQL database dump complete
--

\unrestrict wydkqiIDM6LWcGy1EK244LtEysAlfQdUSSwoS9vdjfXdYYshgdYDmUuAbBk9CMt

