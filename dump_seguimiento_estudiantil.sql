--
-- PostgreSQL database dump
--

\restrict K2C41zklfeXhK5uNGe6MHWVpVcava5n1CIvRDLhhbApOn9oVBWTZZuS579QPWNM

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

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
-- Name: asistencias; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.asistencias (
    id integer NOT NULL,
    inscripcion_id integer NOT NULL,
    fecha date NOT NULL,
    presente boolean,
    justificado boolean,
    observaciones text
);


ALTER TABLE public.asistencias OWNER TO postgres;

--
-- Name: asistencias_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.asistencias_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.asistencias_id_seq OWNER TO postgres;

--
-- Name: asistencias_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.asistencias_id_seq OWNED BY public.asistencias.id;


--
-- Name: ciclos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ciclos (
    id integer NOT NULL,
    nombre character varying(50) NOT NULL,
    codigo_ciclo character varying(20) NOT NULL,
    fecha_inicio date NOT NULL,
    fecha_fin date NOT NULL,
    activo boolean
);


ALTER TABLE public.ciclos OWNER TO postgres;

--
-- Name: ciclos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ciclos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ciclos_id_seq OWNER TO postgres;

--
-- Name: ciclos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ciclos_id_seq OWNED BY public.ciclos.id;


--
-- Name: cursos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cursos (
    id integer NOT NULL,
    codigo_curso character varying(20) NOT NULL,
    nombre_curso character varying(100) NOT NULL,
    creditos integer,
    semestre character varying(10) NOT NULL,
    ciclo_id integer NOT NULL,
    docente_id integer,
    activo boolean
);


ALTER TABLE public.cursos OWNER TO postgres;

--
-- Name: cursos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cursos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cursos_id_seq OWNER TO postgres;

--
-- Name: cursos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cursos_id_seq OWNED BY public.cursos.id;


--
-- Name: estudiantes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.estudiantes (
    id integer NOT NULL,
    codigo_estudiante character varying(20) NOT NULL,
    nombres character varying(100) NOT NULL,
    apellidos character varying(100) NOT NULL,
    email character varying(150) NOT NULL,
    telefono character varying(15),
    fecha_inscripcion date,
    activo boolean
);


ALTER TABLE public.estudiantes OWNER TO postgres;

--
-- Name: estudiantes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.estudiantes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.estudiantes_id_seq OWNER TO postgres;

--
-- Name: estudiantes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.estudiantes_id_seq OWNED BY public.estudiantes.id;


--
-- Name: evaluaciones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.evaluaciones (
    id integer NOT NULL,
    curso_id integer NOT NULL,
    nombre_evaluacion character varying(100) NOT NULL,
    tipo_evaluacion character varying(50),
    peso numeric(5,2),
    fecha_creacion date
);


ALTER TABLE public.evaluaciones OWNER TO postgres;

--
-- Name: evaluaciones_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.evaluaciones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.evaluaciones_id_seq OWNER TO postgres;

--
-- Name: evaluaciones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.evaluaciones_id_seq OWNED BY public.evaluaciones.id;


--
-- Name: inscripciones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.inscripciones (
    id integer NOT NULL,
    estudiante_id integer NOT NULL,
    curso_id integer NOT NULL,
    fecha_inscripcion date,
    estado character varying(20)
);


ALTER TABLE public.inscripciones OWNER TO postgres;

--
-- Name: inscripciones_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.inscripciones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.inscripciones_id_seq OWNER TO postgres;

--
-- Name: inscripciones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.inscripciones_id_seq OWNED BY public.inscripciones.id;


--
-- Name: intervenciones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.intervenciones (
    id integer NOT NULL,
    estudiante_id integer NOT NULL,
    tipo_intervencion character varying(50),
    descripcion text NOT NULL,
    fecha_intervencion date,
    responsable character varying(100),
    estado character varying(20),
    resultado text
);


ALTER TABLE public.intervenciones OWNER TO postgres;

--
-- Name: intervenciones_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.intervenciones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.intervenciones_id_seq OWNER TO postgres;

--
-- Name: intervenciones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.intervenciones_id_seq OWNED BY public.intervenciones.id;


--
-- Name: notas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notas (
    id integer NOT NULL,
    inscripcion_id integer NOT NULL,
    evaluacion_id integer NOT NULL,
    nota numeric(5,2),
    fecha_registro date,
    observaciones text
);


ALTER TABLE public.notas OWNER TO postgres;

--
-- Name: notas_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.notas_id_seq OWNER TO postgres;

--
-- Name: notas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notas_id_seq OWNED BY public.notas.id;


--
-- Name: reportes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reportes (
    id integer NOT NULL,
    tipo_reporte character varying(50) NOT NULL,
    titulo character varying(200) NOT NULL,
    descripcion text,
    parametros json,
    contenido text,
    usuario_id integer NOT NULL,
    fecha_generacion timestamp without time zone,
    archivo_path character varying(500)
);


ALTER TABLE public.reportes OWNER TO postgres;

--
-- Name: reportes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reportes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reportes_id_seq OWNER TO postgres;

--
-- Name: reportes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reportes_id_seq OWNED BY public.reportes.id;


--
-- Name: seguimiento_riesgo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.seguimiento_riesgo (
    id integer NOT NULL,
    estudiante_id integer NOT NULL,
    semestre character varying(10) NOT NULL,
    categoria_riesgo character varying(20),
    puntaje_riesgo numeric(5,2),
    puntaje_anterior numeric(5,2),
    tendencia character varying(20),
    fecha_evaluacion date,
    factores_riesgo json,
    observaciones text
);


ALTER TABLE public.seguimiento_riesgo OWNER TO postgres;

--
-- Name: seguimiento_riesgo_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.seguimiento_riesgo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.seguimiento_riesgo_id_seq OWNER TO postgres;

--
-- Name: seguimiento_riesgo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.seguimiento_riesgo_id_seq OWNED BY public.seguimiento_riesgo.id;


--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuarios (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(128),
    rol character varying(20),
    activo boolean,
    fecha_creacion timestamp without time zone
);


ALTER TABLE public.usuarios OWNER TO postgres;

--
-- Name: usuarios_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.usuarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usuarios_id_seq OWNER TO postgres;

--
-- Name: usuarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.usuarios_id_seq OWNED BY public.usuarios.id;


--
-- Name: asistencias id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asistencias ALTER COLUMN id SET DEFAULT nextval('public.asistencias_id_seq'::regclass);


--
-- Name: ciclos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ciclos ALTER COLUMN id SET DEFAULT nextval('public.ciclos_id_seq'::regclass);


--
-- Name: cursos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cursos ALTER COLUMN id SET DEFAULT nextval('public.cursos_id_seq'::regclass);


--
-- Name: estudiantes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estudiantes ALTER COLUMN id SET DEFAULT nextval('public.estudiantes_id_seq'::regclass);


--
-- Name: evaluaciones id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evaluaciones ALTER COLUMN id SET DEFAULT nextval('public.evaluaciones_id_seq'::regclass);


--
-- Name: inscripciones id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inscripciones ALTER COLUMN id SET DEFAULT nextval('public.inscripciones_id_seq'::regclass);


--
-- Name: intervenciones id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.intervenciones ALTER COLUMN id SET DEFAULT nextval('public.intervenciones_id_seq'::regclass);


--
-- Name: notas id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notas ALTER COLUMN id SET DEFAULT nextval('public.notas_id_seq'::regclass);


--
-- Name: reportes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reportes ALTER COLUMN id SET DEFAULT nextval('public.reportes_id_seq'::regclass);


--
-- Name: seguimiento_riesgo id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.seguimiento_riesgo ALTER COLUMN id SET DEFAULT nextval('public.seguimiento_riesgo_id_seq'::regclass);


--
-- Name: usuarios id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios ALTER COLUMN id SET DEFAULT nextval('public.usuarios_id_seq'::regclass);


--
-- Data for Name: asistencias; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.asistencias (id, inscripcion_id, fecha, presente, justificado, observaciones) FROM stdin;
\.


--
-- Data for Name: ciclos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ciclos (id, nombre, codigo_ciclo, fecha_inicio, fecha_fin, activo) FROM stdin;
1	Ciclo 2026-1	2026-1	2026-07-02	2026-07-02	t
\.


--
-- Data for Name: cursos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cursos (id, codigo_curso, nombre_curso, creditos, semestre, ciclo_id, docente_id, activo) FROM stdin;
1	LP101	Lenguaje de programación	4	I	1	\N	t
2	DMLP102	Diagnostico y Mantenimiento lógico de PC.	4	I	1	\N	t
3	ADS201	Analisis y diseño de sistemas	2	II	1	\N	t
4	FP202	Fundamentos de Programación	3	II	1	\N	t
5	PCRETI103	Planificación y Configuración de Redes en Entornos TI	3	I	1	\N	t
6	HPD203	Herramientas de Programación Distribuida	2	II	1	\N	t
7	HPC204	Herramientas de  Programación Concurrente	2	II	1	\N	t
8	AS205	Administracion de Servidores	3	II	1	\N	t
9	AE104	Aplicaciones Empresariales	4	I	1	\N	t
10	LP206	Lógica de Programación	2	II	1	\N	t
11	CO105	Comunicación oral	2	I	1	\N	t
12	IPT207	Interpretación y producción textos 	2	II	1	\N	t
13	AI106	Aplicaciones en internet 	2	I	1	\N	t
14	O208	Ofimática 	2	II	1	\N	t
15	EFSRT107	Experiencias formativas en situaciones reales de trabajo I	0	I	1	\N	t
16	EFSRT209	Experiencias formativas en situaciones reales de trabajo II	0	II	1	\N	t
17	EFSRT301	Experiencias formativas en situaciones reales de trabajo III	0	III	1	\N	t
18	EFSRT401	Experiencias formativas en situaciones reales de trabajo IV	0	IV	1	\N	t
19	EFSRT501	Experiencias formativas en situaciones reales de trabajo V	0	V	1	\N	t
20	EFSRT601	Experiencias formativas en situaciones reales de trabajo VI	0	VI	1	\N	t
21	EBD302	Estructura de Base de Datos	2	III	1	\N	t
22	IEBD402	Implementacion de estructuras de Base Datos	4	IV	1	\N	t
23	PD303	Programación Distribuida	4	III	1	\N	t
24	PC304	Programación Concurrente	4	III	1	\N	t
25	POO305	Programación Orientada a Objeto	4	III	1	\N	t
26	DSC403	Deasarrollo de software colaborativo	4	IV	1	\N	t
27	SI404	Seguridad Informatica	4	IV	1	\N	t
28	DSG405	Diseño de soluciones gráficas	4	IV	1	\N	t
29	MS306	Modelamiento de Software	2	III	1	\N	t
30	IPCO307	Inglés para la comunicaión oral	2	III	1	\N	t
31	CRI406	Comprensión y redacción en inglés	2	IV	1	\N	t
32	CE308	Comportamiento Ético	2	III	1	\N	t
33	EPRP407	Estrategias para la resolución de problemas	2	IV	1	\N	t
34	GAW502	Gestion y Administración Web	3	V	1	\N	t
35	AG503	Animacion Grafica	3	V	1	\N	t
36	DW504	Diseño Web	4	V	1	\N	t
37	PW602	Programación Web	5	VI	1	\N	t
38	DAM505	Desarrollo de Aplicaciones Moviles	4	V	1	\N	t
39	IAST603	Inteligencia Artificial y Soluciones Tecnológicas	4	VI	1	\N	t
40	IN604	Inteligencia de Negocios	3	VI	1	\N	t
41	PA605	Producción Audiovisual	3	VI	1	\N	t
42	FI506	Fundamentos de innovación	2	V	1	\N	t
43	IT606	Innovación Tecnológica	2	VI	1	\N	t
44	ON507	Oportunidades de negocio	2	V	1	\N	t
45	PL607	Plan de negocios	2	VI	1	\N	t
\.


--
-- Data for Name: estudiantes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.estudiantes (id, codigo_estudiante, nombres, apellidos, email, telefono, fecha_inscripcion, activo) FROM stdin;
1	76716873	Acosta Yzquierdo	Geremi Valentino	valentinoacosta759@gmail.com	923326035	2026-07-02	t
2	73510095	Ahuanari Elizalde	Junior Adriano	ahunariadriano78@gmail.com	943448222	2026-07-02	t
3	63273612	Amaringo Reategui	Josias Danidson	amaringoreateguidani@gmail.com	963380996	2026-07-02	t
4	75933316	Ampuero Tamani	Ashley	ashleyampuero5@gmail.com	968401860	2026-07-02	t
5	74737471	Bernardo Lopez	Jean Franco	jeanfrankithol@gmail.com	926768879	2026-07-02	t
6	66683267	Caballero Valdiviezo	Jahir Smith	jahircaballero1@gmail.com	981974457	2026-07-02	t
7	77049419	Cauper Vasquez	Clara	claracauper37@gmail.com	984204098	2026-07-02	t
8	61122464	Chavez Pinchi	Luis Antonio	chavezpinchiluisantonio@gmail.com	918664824	2026-07-02	t
9	74464010	Chujutalli Calderon	Melany Xiomara	melanyxiomara.005@gmail.com	984121139	2026-07-02	t
10	60633063	Cuzcano Cardenas	Larry Alejandro	larryalejandrocuzcanocardenas@gmai.com	975983787	2026-07-02	t
11	62706953	Da Costa Leonardo	Joseph Joao	josephjoaodacostaleandro@gmai.com	901650024	2026-07-02	t
12	61321611	Del Aguila Fababa	Romel	romeldelaguila95@gmail.com	926114684	2026-07-02	t
13	78947906	Deza Pinedo	Andrea Nicol	dezaandre683@gmail.com	963985876	2026-07-02	t
14	60832298	Dominguez Rengifo	Elizabeth Nicoll	nicolldominguezrengifo@gmail.com	958352871	2026-07-02	t
15	62039173	Escalante Cabanillas	Luis Angel	luisangelescalantecabanillas@gmail.com	984065148	2026-07-02	t
16	81110786	Fasabi Davila	Jeorge Patrick	patrickdavila028@gmail.com	997702688	2026-07-02	t
17	71230233	Flores Grandez	Fernando Samuel	floresgrandezsamuel@gmail.com	959273049	2026-07-02	t
18	61975033	Galindo Diaz	Sahori Yamile	sahorigalindodiaz@gmail.com	931147458	2026-07-02	t
19	62035233	Gomez Acuña	Carmen Nicole	nicole.gomezacuna2009@gmail.com	904884794	2026-07-02	t
20	61379834	Guerra Jones	Piero Luciano	pieroguerra88@gmail.com	993991080	2026-07-02	t
21	61077288	La Torre Gonzales	Thiago	royhumbertolatorrevasquez04@gmail.com	940697210	2026-07-02	t
22	63390321	Linares Sangama	Jayne	jaynelinaressangama20@gmail.com	901295831	2026-07-02	t
23	60710920	Marquez Urquia	Lizania Marilin	urquiamari21@gmail.com	985155848	2026-07-02	t
24	61505104	Maynas Del Aguila	Kristell Kiara	vkristell291@gmail.com	989685770	2026-07-02	t
25	60203684	Mendez Pezo	Cindy	maytemendez235@gmail.com	980103770	2026-07-02	t
26	60014139	Mendez Pezo	Dayanita Mayte	mendezpezod@gmail.com	953033791	2026-07-02	t
27	62035715	Molina Flores	Alex Sandro	alexsandromolina25@gmail.com	966329709	2026-07-02	t
28	60452239	Mora Quispe	Jenifer Sefora	cefota6@gmail.com	942579177	2026-07-02	t
29	61077186	Moreno Hurtado	Angela Ariana	morenoariana2007@gmail.com	982105708	2026-07-02	t
30	75902018	Nolorbe Pasmiño	Karolay Milagros	karolay.15nolorbe@gmail.com	949204881	2026-07-02	t
31	61039800	Nuñez Moreno	Claudia Veronica	claudiaveronica645@gmail.com	932595242	2026-07-02	t
32	61379410	Popolizio Castillo	Jhon Patrick	patriciacastillocisneros.1@gmail.com	949559998	2026-07-02	t
33	73969877	Prada Sinti	Ytati Frisila	ytatiprada09@gmail.com	983736428	2026-07-02	t
34	61546105	Rivera Vasquez	Naomi Nicoll	naomiriverat@gmail.com	958892484	2026-07-02	t
35	61874442	Sotil Carbajal	Dayanna Isabel	isabel.sotil.carbajal@gmail.com	912442636	2026-07-02	t
36	61307623	Vela Sangama	Marcos Andres	andresvelasangama@gmail.com	926033973	2026-07-02	t
37	61245317	Vera Taricuarima	Cecia Abigail	cesiavera118@gmail.com	935279631	2026-07-02	t
38	61820538	Yupanqui Grandez	Hayla Koraly	grandezquintanakoraly@gmail.com	945737582	2026-07-02	t
39	60832237	Arevalo Villacorta	Ricardo	arevalovillacortar@gmail.com	945169962.0	2026-07-02	t
40	61133948	Azañero Villar	Brayan Alexis	azañeroalexis85@agmail.com	974259435.0	2026-07-02	t
41	77415003	Barbaran Gonzales	Jhuel Alejandro	jhuelbarbaran9@gmail.com	978780736.0	2026-07-02	t
42	73546984	Bartra Montalvo	Brayan Piero	ppierobartra@gmail.com	972329017.0	2026-07-02	t
43	61286219	Bolaños Rios	Noelia Estefani	noeliaestefanibolanosrios@gmail.com	958311346.0	2026-07-02	t
44	47024234	Curto Yuyarima	Carito Katiuska	curtocarito@gmail.com	944658461.0	2026-07-02	t
45	61343470	Duque Paniora	Carlos Adrian	adriancitopaniorac@gmail.com	990516065.0	2026-07-02	t
46	61201873	Espinoza Ramirez	Adriano David	adrianoramirez121@gmail.com	932703421.0	2026-07-02	t
47	74191818	Fachin Rojas	Leysglin Riquelmer	riquelmerrojas@gmail.com	951957617.0	2026-07-02	t
48	73630690	Garcia Diaz	Jesus Enrique Alonso	jesusgarciadiaz391@gmail.com	924146969.0	2026-07-02	t
49	61122710	Garcia Gongora	Sandy Margarita	zandyg09@gmail.com	974636828.0	2026-07-02	t
50	78028272	Gatica Saavedra	Jennifer	thiagolucas171121@gmail.com	975090361.0	2026-07-02	t
51	76029422	Gonzales De Souza	Jhonatan Nijar	jhontannijargonzalesdesouza@gmail.com	952293640.0	2026-07-02	t
52	63123442	Huaman Salas	Isai	isaihuamansalas@gmail.com	906702639.0	2026-07-02	t
53	61344131	Isuiza Cahuaza	Nahomi Nieves	nahomiisuiza38@gmail.com	922885954.0	2026-07-02	t
54	76866377	Jacobo Martel	Luz Lizbeth	jluzlizbeth@gmail.com	926647630.0	2026-07-02	t
55	61245580	Lopez Sharihua	Jorge Valentin	lopezvalentino346@gmail.com	915180667.0	2026-07-02	t
56	76498613	Macedo Macedo	Cristiam Saul	cristiamsaul2@gmail.com	958402261.0	2026-07-02	t
57	61201824	Mamani Chino	Benjamin	chino31benjamin@gmail.com	935486964.0	2026-07-02	t
58	61006119	Melgarejo Huaman	Anllely Sileny	silenyhuaman7@gmail.com	957026392.0	2026-07-02	t
59	71238372	Oliveira Huayta	Mayra Tahina	mayratahinaoliveirahuayta19@gmail.com	958687401.0	2026-07-02	t
60	60997000	Panaifo Agustin	Angelo Jhair	angelojhairpanaifoagustin2007@gmail.com	937543544.0	2026-07-02	t
61	60110409	Panduro Ramos	Lucy Ivonny	panduroramoslucy@gmail.com	964665347.0	2026-07-02	t
62	73885601	Perea Saldaña	Carlos Alexis	caps6954@gmail.com	912849419.0	2026-07-02	t
63	72122196	Ramirez Castilla	Luis Elmer	zlkarozr3@gmail.com	986085391.0	2026-07-02	t
64	61122301	Reategui Pinedo	Angel Gabriel	reateguigabriel707@gmail.com	977157725.0	2026-07-02	t
65	81102122	Rioja Vargas	Jastin Isaac	isakvargasss@gmail.com	983003414.0	2026-07-02	t
66	76891264	Rivera Mori	Maxi Leonel	leonelrivera6759684@gmail.com	942244224.0	2026-07-02	t
67	61091944	Rodriguez Cari	Christian Jhoel	christianjhoelrodriguezcari@gmail.com	914756362.0	2026-07-02	t
68	74851201	Rodriguez Rodriguez	Leonardo	leonadoxd12@gmail.com	906329361.0	2026-07-02	t
69	70710170	Rojas Diaz	Piero Alexandro	rojasdiazpiero@gmail.com	912078239.0	2026-07-02	t
70	70967054	Ruiz Pinedo	Hector Alexander	hectorruizpinedo457@gmail.com	975160330.0	2026-07-02	t
71	61006146	Salas Ormeño	Geric Aldair	cuageri10@gmail.com	962002254.0	2026-07-02	t
72	61088684	Sanchez Cumapa	Noemi	nohemysan84@gmail.com	940348776.0	2026-07-02	t
73	61237674	Sandi Nunta	Valerys Brillyth	sandinuntav@gmail.com	948933998.0	2026-07-02	t
74	61077171	Segura Amasifuen	Alex Anderson	Tryhard S Games@gmail.com	902649473.0	2026-07-02	t
75	61040459	Serruche Panduro	Sergio Adrian	sserruchepanduro@gmail.com	982900882.0	2026-07-02	t
76	41654445	Sevillano Flores	John Erick	opensmart1028@gmail.com	981962241.0	2026-07-02	t
77	77433387	Soria Ramirez	Gilmer Wilfredo	soriaramirezwilfredo@gmail.com	976725029.0	2026-07-02	t
78	74799549	Tange Hidalgo	Segundo Geiner	geinertange25@gmail.com	926079342.0	2026-07-02	t
79	60818621	Tapullima Navarro	Tania Lorena	taniaorenatapullimanavarro@gmail.com	972885623.0	2026-07-02	t
80	61133766	Tuanama Severiano	Jhasy Thanie	svr.jhass@gmail.com	996530421.0	2026-07-02	t
81	60014134	Urquia Lopez	Clider	cliderlex@gmail.com	913826706.0	2026-07-02	t
82	75091167	Valdivieso Jorge	Jair Dan	jairdan.1001@gmail.com	946593452.0	2026-07-02	t
83	62431273	Valles Guerra	Jhoy Jahir	jahirvalles00@gmail.com		2026-07-02	t
84	70773913	Vargas Huayunga	Lloner	vargashuayunga92@gmail.com	938252814.0	2026-07-02	t
85	74370827	Vasquez Godoy	Angel Jesus	angeljesusvasquezgodoy663@gmail.com	912785092.0	2026-07-02	t
86	80902538	Zevallos Aliaga	Sammer	sammerzevallos23@gmail.com	933538408.0	2026-07-02	t
87	61379403	Zumaeta Alva	Matias Tiziano	seforanicole7@gmail.com	910875729.0	2026-07-02	t
88	77648746	Cahuana Tello	Leonardo	cahuanatelloleonardo@gmail.com	929608252.0	2026-07-02	t
89	60963473	Culqui Moncada	Emiliano Sebastian	emilianoculqui203@gmail.com	978955810.0	2026-07-02	t
90	73897884	Duque Balabarca	Carlos Andres	duquecarlos716@gmail.com	994279939.0	2026-07-02	t
91	74861005	Flores Taricuarima	Leonardo Ivan	liftper2005@gmail.com	947355256.0	2026-07-02	t
93	75990313	Gonzales Macedo	Ruth Abigail	ruthabigailgonzalesmacedo@gmail.com	929642387.0	2026-07-02	t
94	61077615	Isuiza Herrera	Franklin Daniel	franklin18daniel2007@gmail.com	921678758.0	2026-07-02	t
95	61006046	Lozano Fripp	Fresia Esther Alexandra	fresialozanofripp@gmail.com	961163848.0	2026-07-02	t
96	76779608	Mallma Champi	Elsa Bris	mallmaelsa743@gmail.com	949735936.0	2026-07-02	t
97	75273160	Marin Flores	Wilson	wmflores1@gmail.com	919184892.0	2026-07-02	t
98	47359082	Marquez Sanchez	Sandro Wichi	marquezsanchezsandro10@gmail.com	948161786.0	2026-07-02	t
99	75423275	Maynas Inuma	Cledy Beria	cledymaynas@gmail.com	928393309.0	2026-07-02	t
100	62779851	Medina Maiz	Analy Dariana	Analydarianamedinamaiz@gmail.com	982320630.0	2026-07-02	t
101	77698560	Palomino Porras	Isai Fortunato	palominoporrasisai2006@gmail.com	935854682.0	2026-07-02	t
102	61133509	Pezo Torres	Francisco David	pezotorresfranciscodavid2@gmail.com	982049224.0	2026-07-02	t
103	72720844	Ruiz Salas	Luis Enrique	luisruizsalas01@gmail.com	983850017.0	2026-07-02	t
104	76233162	Ushiñahua Pinedo	Dayana Brillith	dayamaushinahua@gmail.com	970327247.0	2026-07-02	t
105	72772962	Zegarra Caballero	Rodrigo	rodrigozegarra1312@gmail.com	945483862.0	2026-07-02	t
92	76803746	Garcia Cordova	Rowling Anthony	rowlinganthonygarciacordova@gmail.com	922375282	2026-07-02	t
\.


--
-- Data for Name: evaluaciones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.evaluaciones (id, curso_id, nombre_evaluacion, tipo_evaluacion, peso, fecha_creacion) FROM stdin;
1	36	Investigacion Psicologia del color	TRABAJO	10.00	2026-04-24
\.


--
-- Data for Name: inscripciones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.inscripciones (id, estudiante_id, curso_id, fecha_inscripcion, estado) FROM stdin;
1	92	36	2026-04-16	ACTIVO
\.


--
-- Data for Name: intervenciones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.intervenciones (id, estudiante_id, tipo_intervencion, descripcion, fecha_intervencion, responsable, estado, resultado) FROM stdin;
\.


--
-- Data for Name: notas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notas (id, inscripcion_id, evaluacion_id, nota, fecha_registro, observaciones) FROM stdin;
1	1	1	15.00	2026-04-23	cumplio con los parametros del trabajo
\.


--
-- Data for Name: reportes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reportes (id, tipo_reporte, titulo, descripcion, parametros, contenido, usuario_id, fecha_generacion, archivo_path) FROM stdin;
1	INDIVIDUAL_RIESGO	Reporte de Riesgo - Garcia Cordova Rowling Anthony	Reporte individual de riesgo académico para el semestre 2026-1	{"estudiante_id": "92", "semestre": "2026-1", "formato": "html"}	<!DOCTYPE html>\n<html lang="es">\n<head>\n    <meta charset="UTF-8">\n    <title>Reporte Individual de Riesgo - Garcia Cordova Rowling Anthony</title>\n    <style>\n        :root {\n            --primary: #0f172a;\n            --accent: #06b6d4;\n            --success: #10b981;\n            --warning: #f59e0b;\n            --danger: #ef4444;\n            --text-main: #1e293b;\n            --text-muted: #64748b;\n            --bg-light: #f8fafc;\n        }\n\n        body {\n            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;\n            color: var(--text-main);\n            line-height: 1.5;\n            margin: 0;\n            padding: 0;\n            background-color: white;\n        }\n\n        .report-container {\n            max-width: 1000px;\n            margin: 0 auto;\n            padding: 40px;\n        }\n\n        /* Header Institutional */\n        .header {\n            display: flex;\n            justify-content: space-between;\n            align-items: center;\n            border-bottom: 2px solid var(--primary);\n            padding-bottom: 20px;\n            margin-bottom: 30px;\n        }\n\n        .header-left {\n            display: flex;\n            align-items: center;\n        }\n\n        .logo {\n            height: 60px;\n            margin-right: 20px;\n        }\n\n        .inst-name {\n            font-size: 24px;\n            font-weight: 800;\n            color: var(--primary);\n            margin: 0;\n            letter-spacing: -0.5px;\n        }\n\n        .report-title {\n            font-size: 14px;\n            font-weight: 600;\n            color: var(--accent);\n            text-transform: uppercase;\n            margin: 0;\n        }\n\n        .header-right {\n            text-align: right;\n        }\n\n        .meta-info {\n            font-size: 12px;\n            color: var(--text-muted);\n            margin: 2px 0;\n        }\n\n        /* Profile Grid */\n        .profile-grid {\n            display: grid;\n            grid-template-columns: 1fr 1fr;\n            gap: 30px;\n            margin-bottom: 40px;\n            background: var(--bg-light);\n            padding: 25px;\n            border-radius: 12px;\n        }\n\n        .profile-item {\n            display: flex;\n            justify-content: space-between;\n            border-bottom: 1px solid #e2e8f0;\n            padding: 8px 0;\n        }\n\n        .profile-label {\n            font-size: 12px;\n            font-weight: 700;\n            color: var(--text-muted);\n            text-transform: uppercase;\n        }\n\n        .profile-value {\n            font-size: 14px;\n            font-weight: 600;\n            color: var(--primary);\n        }\n\n        /* Risk Dashboard */\n        .risk-dashboard {\n            display: grid;\n            grid-template-columns: repeat(3, 1fr);\n            gap: 20px;\n            margin-bottom: 40px;\n        }\n\n        .risk-card {\n            padding: 25px;\n            border-radius: 12px;\n            text-align: center;\n            color: white;\n        }\n\n        .card-red { background: var(--danger); }\n        .card-yellow { background: var(--warning); }\n        .card-green { background: var(--success); }\n\n        .risk-val {\n            font-size: 32px;\n            font-weight: 800;\n            display: block;\n        }\n\n        .risk-label {\n            font-size: 11px;\n            font-weight: 700;\n            text-transform: uppercase;\n            opacity: 0.9;\n        }\n\n        /* Table */\n        .section-title {\n            font-size: 16px;\n            font-weight: 700;\n            color: var(--primary);\n            margin-bottom: 20px;\n            padding-left: 10px;\n            border-left: 4px solid var(--accent);\n        }\n\n        table {\n            width: 100%;\n            border-collapse: collapse;\n            margin-bottom: 40px;\n        }\n\n        th {\n            background-color: var(--primary);\n            color: white;\n            font-size: 11px;\n            text-transform: uppercase;\n            text-align: left;\n            padding: 12px 15px;\n        }\n\n        td {\n            padding: 12px 15px;\n            font-size: 13px;\n            border-bottom: 1px solid #e2e8f0;\n        }\n\n        .badge {\n            padding: 4px 8px;\n            border-radius: 4px;\n            font-size: 10px;\n            font-weight: 700;\n            text-transform: uppercase;\n        }\n\n        .bg-red { background: #fee2e2; color: #991b1b; }\n        .bg-yellow { background: #fef3c7; color: #92400e; }\n        .bg-green { background: #d1fae5; color: #065f46; }\n\n        /* Recommendations */\n        .analysis-box {\n            background-color: var(--bg-light);\n            border-radius: 12px;\n            padding: 25px;\n            margin-bottom: 40px;\n        }\n\n        .analysis-title {\n            font-size: 14px;\n            font-weight: 700;\n            margin-bottom: 15px;\n            color: var(--primary);\n            display: flex;\n            align-items: center;\n        }\n\n        .analysis-list {\n            margin: 0;\n            padding-left: 20px;\n            font-size: 13px;\n            color: var(--text-main);\n        }\n\n        .analysis-list li {\n            margin-bottom: 10px;\n        }\n\n        /* Signatures */\n        .signatures {\n            display: flex;\n            justify-content: space-between;\n            margin-top: 80px;\n            page-break-inside: avoid;\n        }\n\n        .sig-block {\n            width: 40%;\n            text-align: center;\n        }\n\n        .sig-line {\n            border-top: 1px solid var(--primary);\n            margin-bottom: 10px;\n        }\n\n        .sig-label {\n            font-size: 12px;\n            font-weight: 700;\n            color: var(--primary);\n        }\n\n        .sig-sub {\n            font-size: 11px;\n            color: var(--text-muted);\n        }\n\n        @media print {\n            .report-container { padding: 0; }\n            .no-print { display: none !important; }\n            @page { margin: 1.5cm; }\n        }\n    </style>\n</head>\n<body>\n    <div class="report-container">\n        <!-- Header -->\n        <div class="header">\n            <div class="header-left">\n                <img src="http://127.0.0.1:5000/static/img/logo_see_f.png" alt="SADES" class="logo">\n                <div>\n                    <h1 class="inst-name">SADES</h1>\n                    <p class="report-title">Expediente de Seguimiento Académico</p>\n                </div>\n            </div>\n            <div class="header-right">\n                <p class="meta-info"><strong>REPORTE:</strong> INDIVIDUAL DE RIESGO</p>\n                <p class="meta-info"><strong>SEMESTRE:</strong> 2026-1</p>\n                <p class="meta-info"><strong>FECHA:</strong> 02/07/2026 13:51</p>\n            </div>\n        </div>\n\n        <!-- Section 1: Profile -->\n        <h2 class="section-title">Perfil del Estudiante</h2>\n        <div class="profile-grid">\n            <div class="profile-col">\n                <div class="profile-item">\n                    <span class="profile-label">Nombre Completo</span>\n                    <span class="profile-value">Garcia Cordova Rowling Anthony</span>\n                </div>\n                <div class="profile-item">\n                    <span class="profile-label">Código</span>\n                    <span class="profile-value">76803746</span>\n                </div>\n                <div class="profile-item">\n                    <span class="profile-label">Correo Institucional</span>\n                    <span class="profile-value">rowlinganthonygarciacordova@gmail.com</span>\n                </div>\n            </div>\n            <div class="profile-col">\n                <div class="profile-item">\n                    <span class="profile-label">Teléfono</span>\n                    <span class="profile-value">922375282</span>\n                </div>\n                <div class="profile-item">\n                    <span class="profile-label">Ingreso</span>\n                    <span class="profile-value">02/07/2026</span>\n                </div>\n                <div class="profile-item">\n                    <span class="profile-label">Estado</span>\n                    <span class="profile-value">ACTIVO</span>\n                </div>\n            </div>\n        </div>\n\n        <!-- Section 2: Risk Level -->\n        <h2 class="section-title">Nivel de Riesgo Detectado</h2>\n        \n        <div class="risk-dashboard">\n            <div class="risk-card card-green">\n                <span class="risk-val">SIN RIESGO</span>\n                <span class="risk-label">Categoría Actual</span>\n            </div>\n            <div class="risk-card" style="background: var(--primary);">\n                <span class="risk-val">0.39</span>\n                <span class="risk-label">Puntaje Algorítmico</span>\n            </div>\n            <div class="risk-card" style="background: var(--accent);">\n                <span class="risk-val">02/07/2026</span>\n                <span class="risk-label">Última Evaluación</span>\n            </div>\n        </div>\n        \n\n        <!-- Section 3: Detailed Performance -->\n        <h2 class="section-title">Desempeño por Asignatura</h2>\n        \n        <p class="text-muted">No se registran cursos inscritos en el semestre analizado.</p>\n        \n\n        <!-- Section 4: Recommendations -->\n        \n        <div class="analysis-box">\n            <h3 class="analysis-title">Plan de Acompañamiento Sugerido</h3>\n            <ul class="analysis-list">\n                \n                    \n                \n                    \n                \n                    \n                \n                    \n                \n                \n                \n            </ul>\n        </div>\n        \n\n        <!-- Signatures -->\n        <div class="signatures">\n            <div class="sig-block">\n                <div class="sig-line"></div>\n                <div class="sig-label">Coordinación Académica</div>\n                <div class="sig-sub">Nombre y Firma</div>\n            </div>\n            <div class="sig-block">\n                <div class="sig-line"></div>\n                <div class="sig-label">Estudiante</div>\n                <div class="sig-sub">Garcia Cordova Rowling Anthony</div>\n            </div>\n        </div>\n    </div>\n</body>\n</html>	1	2026-07-02 13:51:34.967861	\N
\.


--
-- Data for Name: seguimiento_riesgo; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.seguimiento_riesgo (id, estudiante_id, semestre, categoria_riesgo, puntaje_riesgo, puntaje_anterior, tendencia, fecha_evaluacion, factores_riesgo, observaciones) FROM stdin;
1	1	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
2	2	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
3	3	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
4	4	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
5	5	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
6	6	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
7	7	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
8	8	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
9	9	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
10	10	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
11	11	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
12	12	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
13	13	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
14	14	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
15	15	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
16	16	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
17	17	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
18	18	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
19	19	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
20	20	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
21	21	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
22	22	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
23	23	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
24	24	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
25	25	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
26	26	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
27	27	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
28	28	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
29	29	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
30	30	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
31	31	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
32	32	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
33	33	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
34	34	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
35	35	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
36	36	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
37	37	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
38	38	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
39	39	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
40	40	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
41	41	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
42	42	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
43	43	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
44	44	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
45	45	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
46	46	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
47	47	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
48	48	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
49	49	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
50	50	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
51	51	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
52	52	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
53	53	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
54	54	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
55	55	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
56	56	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
57	57	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
58	58	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
59	59	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
60	60	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
61	61	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
62	62	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
63	63	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
64	64	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
65	65	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
66	66	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
67	67	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
68	68	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
69	69	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
70	70	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
71	71	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
72	72	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
73	73	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
74	74	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
75	75	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
82	82	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
83	83	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
84	84	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
85	85	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
86	86	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
87	87	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
76	76	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
77	77	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
78	78	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
79	79	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
80	80	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
81	81	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
88	88	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
89	89	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
90	90	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
91	91	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
92	92	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
93	93	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
94	94	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
95	95	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
96	96	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
97	97	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
98	98	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
99	99	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
100	100	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
101	101	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
102	102	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
103	103	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
104	104	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
105	105	2026-1	SIN_RIESGO	0.39	0.39	ESTABLE	2026-07-02	[{"nombre": "Rendimiento Actual", "valor": 0.5, "peso": 0.35, "descripcion": "Sin cursos inscritos", "contribucion": 0.175}, {"nombre": "Asistencia Actual", "valor": 0.2, "peso": 0.25, "descripcion": "Sin registros de asistencia", "contribucion": 0.05}, {"nombre": "Distribuci\\u00f3n de Riesgo", "valor": 0.5, "peso": 0.2, "descripcion": "Sin cursos inscritos", "contribucion": 0.1}, {"nombre": "Historial Acad\\u00e9mico", "valor": 0.3, "peso": 0.2, "descripcion": "Estudiante nuevo (Sin historial)", "contribucion": 0.06}]	\N
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuarios (id, username, email, password_hash, rol, activo, fecha_creacion) FROM stdin;
1	admin	admin@sades.edu	pbkdf2:sha256:600000$gVWIhcT8s2aSy5Gb$9b2b767b3fbf93b302085317cafa3f948285f41a365c8d4861d45fabbbaed681	administrador	t	2026-07-02 03:15:27.973168
\.


--
-- Name: asistencias_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.asistencias_id_seq', 1, false);


--
-- Name: ciclos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.ciclos_id_seq', 1, true);


--
-- Name: cursos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cursos_id_seq', 45, true);


--
-- Name: estudiantes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.estudiantes_id_seq', 105, true);


--
-- Name: evaluaciones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.evaluaciones_id_seq', 1, true);


--
-- Name: inscripciones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.inscripciones_id_seq', 1, true);


--
-- Name: intervenciones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.intervenciones_id_seq', 1, false);


--
-- Name: notas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.notas_id_seq', 1, true);


--
-- Name: reportes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reportes_id_seq', 1, true);


--
-- Name: seguimiento_riesgo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.seguimiento_riesgo_id_seq', 105, true);


--
-- Name: usuarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usuarios_id_seq', 1, true);


--
-- Name: asistencias asistencias_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asistencias
    ADD CONSTRAINT asistencias_pkey PRIMARY KEY (id);


--
-- Name: ciclos ciclos_codigo_ciclo_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ciclos
    ADD CONSTRAINT ciclos_codigo_ciclo_key UNIQUE (codigo_ciclo);


--
-- Name: ciclos ciclos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ciclos
    ADD CONSTRAINT ciclos_pkey PRIMARY KEY (id);


--
-- Name: cursos cursos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cursos
    ADD CONSTRAINT cursos_pkey PRIMARY KEY (id);


--
-- Name: estudiantes estudiantes_codigo_estudiante_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estudiantes
    ADD CONSTRAINT estudiantes_codigo_estudiante_key UNIQUE (codigo_estudiante);


--
-- Name: estudiantes estudiantes_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estudiantes
    ADD CONSTRAINT estudiantes_email_key UNIQUE (email);


--
-- Name: estudiantes estudiantes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estudiantes
    ADD CONSTRAINT estudiantes_pkey PRIMARY KEY (id);


--
-- Name: evaluaciones evaluaciones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evaluaciones
    ADD CONSTRAINT evaluaciones_pkey PRIMARY KEY (id);


--
-- Name: inscripciones inscripciones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inscripciones
    ADD CONSTRAINT inscripciones_pkey PRIMARY KEY (id);


--
-- Name: intervenciones intervenciones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.intervenciones
    ADD CONSTRAINT intervenciones_pkey PRIMARY KEY (id);


--
-- Name: notas notas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notas
    ADD CONSTRAINT notas_pkey PRIMARY KEY (id);


--
-- Name: reportes reportes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reportes
    ADD CONSTRAINT reportes_pkey PRIMARY KEY (id);


--
-- Name: seguimiento_riesgo seguimiento_riesgo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.seguimiento_riesgo
    ADD CONSTRAINT seguimiento_riesgo_pkey PRIMARY KEY (id);


--
-- Name: cursos uq_curso_ciclo; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cursos
    ADD CONSTRAINT uq_curso_ciclo UNIQUE (codigo_curso, ciclo_id);


--
-- Name: usuarios usuarios_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_email_key UNIQUE (email);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);


--
-- Name: usuarios usuarios_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_username_key UNIQUE (username);


--
-- Name: asistencias asistencias_inscripcion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asistencias
    ADD CONSTRAINT asistencias_inscripcion_id_fkey FOREIGN KEY (inscripcion_id) REFERENCES public.inscripciones(id);


--
-- Name: cursos cursos_ciclo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cursos
    ADD CONSTRAINT cursos_ciclo_id_fkey FOREIGN KEY (ciclo_id) REFERENCES public.ciclos(id);


--
-- Name: cursos cursos_docente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cursos
    ADD CONSTRAINT cursos_docente_id_fkey FOREIGN KEY (docente_id) REFERENCES public.usuarios(id);


--
-- Name: evaluaciones evaluaciones_curso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evaluaciones
    ADD CONSTRAINT evaluaciones_curso_id_fkey FOREIGN KEY (curso_id) REFERENCES public.cursos(id);


--
-- Name: inscripciones inscripciones_curso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inscripciones
    ADD CONSTRAINT inscripciones_curso_id_fkey FOREIGN KEY (curso_id) REFERENCES public.cursos(id);


--
-- Name: inscripciones inscripciones_estudiante_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inscripciones
    ADD CONSTRAINT inscripciones_estudiante_id_fkey FOREIGN KEY (estudiante_id) REFERENCES public.estudiantes(id);


--
-- Name: intervenciones intervenciones_estudiante_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.intervenciones
    ADD CONSTRAINT intervenciones_estudiante_id_fkey FOREIGN KEY (estudiante_id) REFERENCES public.estudiantes(id);


--
-- Name: notas notas_evaluacion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notas
    ADD CONSTRAINT notas_evaluacion_id_fkey FOREIGN KEY (evaluacion_id) REFERENCES public.evaluaciones(id);


--
-- Name: notas notas_inscripcion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notas
    ADD CONSTRAINT notas_inscripcion_id_fkey FOREIGN KEY (inscripcion_id) REFERENCES public.inscripciones(id);


--
-- Name: reportes reportes_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reportes
    ADD CONSTRAINT reportes_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id);


--
-- Name: seguimiento_riesgo seguimiento_riesgo_estudiante_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.seguimiento_riesgo
    ADD CONSTRAINT seguimiento_riesgo_estudiante_id_fkey FOREIGN KEY (estudiante_id) REFERENCES public.estudiantes(id);


--
-- PostgreSQL database dump complete
--

\unrestrict K2C41zklfeXhK5uNGe6MHWVpVcava5n1CIvRDLhhbApOn9oVBWTZZuS579QPWNM

