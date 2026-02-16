--
-- PostgreSQL database dump
--

\restrict D2ildhNWoHP3jKg7hgDSfBnNiaxu34779XAnQz0clEcC9EFbDKZPhYF6Q4FjXFt

-- Dumped from database version 16.11 (Debian 16.11-1.pgdg13+1)
-- Dumped by pg_dump version 16.11 (Debian 16.11-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
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
-- Name: accounts; Type: TABLE; Schema: public; Owner: banco_user
--

CREATE TABLE public.accounts (
    id integer NOT NULL,
    customer_id integer NOT NULL,
    type character varying NOT NULL,
    balance double precision NOT NULL
);


ALTER TABLE public.accounts OWNER TO banco_user;

--
-- Name: accounts_id_seq; Type: SEQUENCE; Schema: public; Owner: banco_user
--

CREATE SEQUENCE public.accounts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.accounts_id_seq OWNER TO banco_user;

--
-- Name: accounts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: banco_user
--

ALTER SEQUENCE public.accounts_id_seq OWNED BY public.accounts.id;


--
-- Name: movements; Type: TABLE; Schema: public; Owner: banco_user
--

CREATE TABLE public.movements (
    id integer NOT NULL,
    account_id integer NOT NULL,
    customer_id integer NOT NULL,
    account_type character varying,
    date character varying NOT NULL,
    description character varying NOT NULL,
    amount double precision NOT NULL,
    type character varying NOT NULL
);


ALTER TABLE public.movements OWNER TO banco_user;

--
-- Name: movements_id_seq; Type: SEQUENCE; Schema: public; Owner: banco_user
--

CREATE SEQUENCE public.movements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.movements_id_seq OWNER TO banco_user;

--
-- Name: movements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: banco_user
--

ALTER SEQUENCE public.movements_id_seq OWNED BY public.movements.id;


--
-- Name: pse_transactions; Type: TABLE; Schema: public; Owner: banco_user
--

CREATE TABLE public.pse_transactions (
    id integer NOT NULL,
    internal_order_id character varying(64) NOT NULL,
    customer_id integer NOT NULL,
    account_id integer NOT NULL,
    amount double precision NOT NULL,
    currency character varying(10) NOT NULL,
    status character varying(20) NOT NULL,
    provider character varying(50) NOT NULL,
    provider_tx_id character varying(100),
    provider_reference character varying(100),
    payment_url character varying,
    callback_status_raw character varying,
    return_url_success character varying,
    return_url_failure character varying,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    expires_at timestamp without time zone
);


ALTER TABLE public.pse_transactions OWNER TO banco_user;

--
-- Name: pse_transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: banco_user
--

CREATE SEQUENCE public.pse_transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pse_transactions_id_seq OWNER TO banco_user;

--
-- Name: pse_transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: banco_user
--

ALTER SEQUENCE public.pse_transactions_id_seq OWNED BY public.pse_transactions.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: banco_user
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying NOT NULL,
    hashed_password character varying NOT NULL
);


ALTER TABLE public.users OWNER TO banco_user;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: banco_user
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO banco_user;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: banco_user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: wallets; Type: TABLE; Schema: public; Owner: banco_user
--

CREATE TABLE public.wallets (
    id integer NOT NULL,
    customer_id integer NOT NULL,
    balance double precision NOT NULL
);


ALTER TABLE public.wallets OWNER TO banco_user;

--
-- Name: wallets_id_seq; Type: SEQUENCE; Schema: public; Owner: banco_user
--

CREATE SEQUENCE public.wallets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.wallets_id_seq OWNER TO banco_user;

--
-- Name: wallets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: banco_user
--

ALTER SEQUENCE public.wallets_id_seq OWNED BY public.wallets.id;


--
-- Name: accounts id; Type: DEFAULT; Schema: public; Owner: banco_user
--

ALTER TABLE ONLY public.accounts ALTER COLUMN id SET DEFAULT nextval('public.accounts_id_seq'::regclass);


--
-- Name: movements id; Type: DEFAULT; Schema: public; Owner: banco_user
--

ALTER TABLE ONLY public.movements ALTER COLUMN id SET DEFAULT nextval('public.movements_id_seq'::regclass);


--
-- Name: pse_transactions id; Type: DEFAULT; Schema: public; Owner: banco_user
--

ALTER TABLE ONLY public.pse_transactions ALTER COLUMN id SET DEFAULT nextval('public.pse_transactions_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: banco_user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: wallets id; Type: DEFAULT; Schema: public; Owner: banco_user
--

ALTER TABLE ONLY public.wallets ALTER COLUMN id SET DEFAULT nextval('public.wallets_id_seq'::regclass);


--
-- Data for Name: accounts; Type: TABLE DATA; Schema: public; Owner: banco_user
--

COPY public.accounts (id, customer_id, type, balance) FROM stdin;
2	100	corriente	30
1	100	ahorros	37.75
3	101	ahorros	39.99999999999978
\.


--
-- Data for Name: movements; Type: TABLE DATA; Schema: public; Owner: banco_user
--

COPY public.movements (id, account_id, customer_id, account_type, date, description, amount, type) FROM stdin;
1	1	100	ahorros	2025-11-15	Nómina	1200	credito
2	1	100	ahorros	2025-11-16	Pago supermercado	150.5	debito
3	2	100	corriente	2025-11-17	Pago tarjeta de crédito	300	debito
4	2	100	corriente	2025-11-18	Transferencia recibida	500	credito
5	3	101	ahorros	2025-11-14	Depósito en efectivo	2000	credito
6	3	101	ahorros	2025-11-19	Pago servicios públicos	220.75	debito
7	2	100	corriente	2025-11-24	Transferencia enviada a cuenta 1	100	debito
8	1	100	ahorros	2025-11-24	Transferencia recibida desde cuenta 2	100	credito
9	2	100	corriente	2025-11-24	Transferencia enviada a cuenta 1	100	debito
10	1	100	ahorros	2025-11-24	Transferencia recibida desde cuenta 2	100	credito
11	1	100	ahorros	2025-11-24	Transferencia enviada a cuenta 2	100	debito
12	2	100	corriente	2025-11-24	Transferencia recibida desde cuenta 1	100	credito
13	1	100	ahorros	2025-11-24	Transferencia enviada a cuenta 2	100	debito
14	2	100	corriente	2025-11-24	Transferencia recibida desde cuenta 1	100	credito
15	2	100	corriente	2025-11-24	Transferencia enviada a cuenta 3	100	debito
16	3	101	ahorros	2025-11-24	Transferencia recibida desde cuenta 2	100	credito
17	3	101	ahorros	2025-12-03	Transferencia enviada a cuenta 2	10	debito
18	2	100	corriente	2025-12-03	Transferencia recibida desde cuenta 3	10	credito
19	1	100	ahorros	2025-12-04	Transferencia enviada a cuenta 3	100	debito
20	3	101	ahorros	2025-12-04	Transferencia recibida desde cuenta 1	100	credito
21	1	100	ahorros	2026-02-08	Transferencia enviada a cuenta 2	10	debito
22	2	100	corriente	2026-02-08	Transferencia recibida desde cuenta 1	10	credito
23	3	101	ahorros	2026-02-08	Transferencia enviada a cuenta 2	10	debito
24	2	100	corriente	2026-02-08	Transferencia recibida desde cuenta 3	10	credito
25	2	100	corriente	2026-02-08	Transferencia enviada a cuenta 3	50	debito
26	3	101	ahorros	2026-02-08	Transferencia recibida desde cuenta 2	50	credito
27	3	101	ahorros	2026-02-08	Transferencia enviada a cuenta 2	10	debito
28	2	100	corriente	2026-02-08	Transferencia recibida desde cuenta 3	10	credito
29	1	100	ahorros	2026-02-12	Transferencia enviada a cuenta 3	10	debito
30	3	101	ahorros	2026-02-12	Transferencia recibida desde cuenta 1	10	credito
\.


--
-- Data for Name: pse_transactions; Type: TABLE DATA; Schema: public; Owner: banco_user
--

COPY public.pse_transactions (id, internal_order_id, customer_id, account_id, amount, currency, status, provider, provider_tx_id, provider_reference, payment_url, callback_status_raw, return_url_success, return_url_failure, created_at, updated_at, expires_at) FROM stdin;
1	PSE-8e52ee91b9d047cc9812	100	1	1	COP	PENDING	PSE	\N	\N	https://sandbox.pse.fake/pay/PSE-8e52ee91b9d047cc9812	\N	http://3.238.129.183/pse/resultado?status=success	http://3.238.129.183/pse/resultado?status=failure	2025-11-24 00:29:32.62156	2025-11-24 00:29:32.621564	2025-11-24 00:44:32.621566
2	PSE-2d3607539c604bedb04b	100	1	1	COP	PENDING	PSE	\N	\N	https://sandbox.pse.fake/pay/PSE-2d3607539c604bedb04b	\N	http://3.238.129.183/pse/resultado?status=success	http://3.238.129.183/pse/resultado?status=failure	2025-11-24 01:45:53.516906	2025-11-24 01:45:53.51691	2025-11-24 02:00:53.516912
3	PSE-0e342b3bed12412aa788	100	1	1	COP	PENDING	PSE	\N	\N	http://banco_fastapi:8000/pse-gateway/PSE-0e342b3bed12412aa788	\N	http://3.238.129.183/pse/resultado?status=success	http://3.238.129.183/pse/resultado?status=failure	2025-11-24 02:18:40.70682	2025-11-24 02:18:40.706824	2025-11-24 02:33:40.706826
4	PSE-da5e140011844291ac40	100	1	10	COP	PENDING	PSE	\N	\N	http://banco_fastapi:8000/pse-gateway/PSE-da5e140011844291ac40	\N	http://3.238.129.183/pse/resultado?status=success	http://3.238.129.183/pse/resultado?status=failure	2025-11-24 02:37:05.428453	2025-11-24 02:37:05.428457	2025-11-24 02:52:05.428459
5	PSE-4e276e0dcae445a88a1b	100	1	1	COP	PENDING	PSE	\N	\N		\N	http://3.238.129.183/pse/resultado?status=success	http://3.238.129.183/pse/resultado?status=failure	2025-11-24 02:45:58.395143	2025-11-24 02:45:58.395146	2025-11-24 03:00:58.395148
6	PSE-c2f365ea5cf242b2986d	100	2	100	COP	PENDING	PSE	\N	\N		\N	http://3.238.129.183/pse/resultado?status=success	http://3.238.129.183/pse/resultado?status=failure	2025-11-24 02:46:36.416632	2025-11-24 02:46:36.416635	2025-11-24 03:01:36.416637
7	PSE-c3f6b84f89354eb88725	100	1	1	COP	PENDING	PSE	\N	\N		\N	http://3.238.129.183/pse/resultado?status=success	http://3.238.129.183/pse/resultado?status=failure	2025-11-24 02:54:11.171383	2025-11-24 02:54:11.171388	2025-11-24 03:09:11.171389
8	PSE-8869212775e24a469d26	100	1	1	COP	PENDING	PSE	\N	\N		\N	http://3.238.129.183/pse/resultado?status=success	http://3.238.129.183/pse/resultado?status=failure	2025-11-24 03:15:58.856751	2025-11-24 03:15:58.856756	2025-11-24 03:30:58.856758
9	PSE-952fc9617af1442f8736	100	2	10	COP	PENDING	PSE	\N	\N		\N	http://3.238.129.183/pse/resultado?status=success	http://3.238.129.183/pse/resultado?status=failure	2025-11-24 03:32:31.892163	2025-11-24 03:32:31.892168	2025-11-24 03:47:31.89217
10	PSE-26dd0a67eca84dd689d7	100	1	9	COP	PENDING	PSE	\N	\N		\N	http://3.238.129.183/pse/resultado?status=success	http://3.238.129.183/pse/resultado?status=failure	2025-11-24 03:32:58.966814	2025-11-24 03:32:58.966817	2025-11-24 03:47:58.966819
11	PSE-10230fc8c35942ab9b4f	100	1	1	COP	PENDING	PSE	\N	\N		\N	http://3.238.129.183/pse/resultado?status=success	http://3.238.129.183/pse/resultado?status=failure	2025-11-24 03:38:52.846791	2025-11-24 03:38:52.846796	2025-11-24 03:53:52.846797
12	PSE-664c608da75347a190a0	100	1	100	COP	PENDING	PSE	\N	\N		\N	http://3.238.129.183/pse/resultado?status=success	http://3.238.129.183/pse/resultado?status=failure	2025-11-24 03:39:15.447541	2025-11-24 03:39:15.447546	2025-11-24 03:54:15.447547
13	PSE-e905afb9883b4ea99132	100	1	100	COP	PENDING	PSE	\N	\N		\N	http://3.238.129.183/pse/resultado?status=success	http://3.238.129.183/pse/resultado?status=failure	2025-11-24 03:39:17.186472	2025-11-24 03:39:17.186475	2025-11-24 03:54:17.186477
14	PSE-987310b6e42a4a1987ff	100	1	100	COP	PENDING	PSE	\N	\N		\N	http://3.238.129.183/pse/resultado?status=success	http://3.238.129.183/pse/resultado?status=failure	2025-11-24 03:42:43.024856	2025-11-24 03:42:43.02486	2025-11-24 03:57:43.024861
15	PSE-e1ce20224ae742d1b45b	100	1	12	COP	PENDING	PSE	\N	\N		\N	http://3.238.129.183/pse/resultado?status=success	http://3.238.129.183/pse/resultado?status=failure	2025-11-24 03:47:35.476231	2025-11-24 03:47:35.476235	2025-11-24 04:02:35.476237
16	PSE-6400d62831d242b8bc82	100	1	12	COP	PENDING	PSE	\N	\N		\N	http://3.238.129.183/pse/resultado?status=success	http://3.238.129.183/pse/resultado?status=failure	2025-11-24 03:53:12.751667	2025-11-24 03:53:12.751672	2025-11-24 04:08:12.751674
17	PSE-a2a1dab09e1a4ee9801f	100	1	100	COP	APPROVED	PSE	\N	\N		\N	http://3.238.129.183/pse/resultado?status=success	http://3.238.129.183/pse/resultado?status=failure	2025-11-24 04:04:06.011277	2025-11-24 04:04:06.203719	2025-11-24 04:19:06.011283
18	PSE-7f3743863fc14b28bf62	100	1	100	COP	APPROVED	PSE	\N	\N		\N	http://3.238.129.183/pse/resultado?status=success	http://3.238.129.183/pse/resultado?status=failure	2025-11-24 04:05:58.406686	2025-11-24 04:05:58.614164	2025-11-24 04:20:58.406692
19	PSE-c72320376f464a23a79d	100	1	1	COP	APPROVED	PSE	\N	\N		\N	http://3.238.129.183/pse/resultado?status=success	http://3.238.129.183/pse/resultado?status=failure	2025-11-24 04:22:00.07135	2025-11-24 04:22:00.263393	2025-11-24 04:37:00.071357
20	PSE-df55f5c3c5a24e2eac25	101	3	1	COP	APPROVED	PSE	\N	\N		\N	http://3.238.129.183/pse/resultado?status=success	http://3.238.129.183/pse/resultado?status=failure	2025-11-24 04:29:25.428245	2025-11-24 04:29:25.635305	2025-11-24 04:44:25.428252
21	PSE-38f41887ec764bb2b775	101	3	1	COP	APPROVED	PSE	\N	\N		\N	http://3.238.129.183/pse/resultado?status=success	http://3.238.129.183/pse/resultado?status=failure	2025-11-24 04:35:53.899243	2025-11-24 04:35:54.106358	2025-11-24 04:50:53.899249
22	PSE-773fbdd4432d44289dcf	101	3	1	COP	APPROVED	PSE	\N	\N		\N	http://3.238.129.183/pse/resultado?status=success	http://3.238.129.183/pse/resultado?status=failure	2025-11-24 04:36:34.856417	2025-11-24 04:36:35.052314	2025-11-24 04:51:34.856424
23	PSE-46f755b0c4d744fcb526	101	3	1	COP	REJECTED	PSE	\N	\N		\N	http://3.238.129.183/pse/resultado?status=success	http://3.238.129.183/pse/resultado?status=failure	2025-11-24 04:46:17.777854	2025-11-24 04:46:17.984893	2025-11-24 05:01:17.777861
24	PSE-4a6efaa070564abfaecd	101	3	1	COP	APPROVED	PSE	\N	\N		\N	http://3.238.129.183/pse/resultado?status=success&amount=1.0&account_id=3	http://3.238.129.183/pse/resultado?status=failure&amount=1.0&account_id=3	2025-11-24 05:03:53.993014	2025-11-24 05:03:54.199845	2025-11-24 05:18:53.993021
25	PSE-d77453a126cd4d3b9072	101	3	1	COP	APPROVED	PSE	\N	\N		\N	http://3.238.129.183/pse/resultado?status=success&amount=1.0&account_id=3	http://3.238.129.183/pse/resultado?status=failure&amount=1.0&account_id=3	2025-11-24 05:12:27.457922	2025-11-24 05:12:27.656428	2025-11-24 05:27:27.457929
26	PSE-fe62eed00f93492d8a5f	101	3	1	COP	APPROVED	PSE	\N	\N		\N	http://3.238.129.183/pse/resultado?status=success&amount=1.0&account_id=3	http://3.238.129.183/pse/resultado?status=failure&amount=1.0&account_id=3	2025-11-24 05:14:43.524807	2025-11-24 05:14:43.72881	2025-11-24 05:29:43.524814
27	PSE-f80c4c0750cb446fa86b	101	3	1	COP	APPROVED	PSE	\N	\N		\N	http://3.238.129.183/pse/resultado?status=success&amount=1.0&account_id=3	http://3.238.129.183/pse/resultado?status=failure&amount=1.0&account_id=3	2025-11-24 05:15:11.486445	2025-11-24 05:15:11.680264	2025-11-24 05:30:11.486452
28	PSE-196b1e4e90f84a77a159	101	3	1	COP	APPROVED	PSE	\N	\N		\N	http://3.238.129.183/pse/resultado?status=success&amount=1.0&account_id=3	http://3.238.129.183/pse/resultado?status=failure&amount=1.0&account_id=3	2025-11-24 05:15:30.10478	2025-11-24 05:15:30.291451	2025-11-24 05:30:30.104786
29	PSE-a6fabbb0e643407e822e	101	3	1	COP	APPROVED	PSE	\N	\N		\N	http://3.238.129.183/pse/resultado?status=success&amount=1.0&account_id=3	http://3.238.129.183/pse/resultado?status=failure&amount=1.0&account_id=3	2025-11-24 05:16:15.466554	2025-11-24 05:16:15.657621	2025-11-24 05:31:15.466562
30	PSE-d88867e7026b46788ca1	101	3	9990	COP	APPROVED	PSE	\N	\N		\N	http://3.238.129.183/pse/resultado?status=success&amount=9990.0&account_id=3	http://3.238.129.183/pse/resultado?status=failure&amount=9990.0&account_id=3	2025-11-24 05:16:35.005819	2025-11-24 05:16:35.194547	2025-11-24 05:31:35.005827
31	PSE-45d346d68c784882b60e	101	3	1	COP	APPROVED	PSE	\N	\N		\N	http://3.238.129.183/pse/resultado?status=success&amount=1.0&account_id=3	http://3.238.129.183/pse/resultado?status=failure&amount=1.0&account_id=3	2025-11-24 05:19:30.300513	2025-11-24 05:19:30.487018	2025-11-24 05:34:30.30052
32	PSE-44c14576d17047ac8ac6	101	3	10	COP	APPROVED	PSE	\N	\N		\N	http://13.217.221.47/pse/resultado?status=success&amount=10.0&account_id=3	http://13.217.221.47/pse/resultado?status=failure&amount=10.0&account_id=3	2025-11-27 00:56:52.497942	2025-11-27 00:56:52.881303	2025-11-27 01:11:52.497949
33	PSE-0aa5f7a460b045e68d10	101	3	10	COP	APPROVED	PSE	\N	\N		\N	http://13.217.221.47/pse/resultado?status=success&amount=10.0&account_id=3	http://13.217.221.47/pse/resultado?status=failure&amount=10.0&account_id=3	2025-11-27 01:19:32.84684	2025-11-27 01:19:33.182083	2025-11-27 01:34:32.846858
34	PSE-99430fa770c045309171	101	3	1	COP	APPROVED	PSE	\N	\N		\N	http://13.217.221.47/pse/resultado?status=success&amount=1.0&account_id=3	http://13.217.221.47/pse/resultado?status=failure&amount=1.0&account_id=3	2025-11-28 02:34:09.704061	2025-11-28 02:34:09.921854	2025-11-28 02:49:09.704069
35	PSE-ec43e62abc94463aa489	100	1	1	COP	APPROVED	PSE	\N	\N		\N	http://13.217.221.47/pse/resultado?status=success&amount=1.0&account_id=1	http://13.217.221.47/pse/resultado?status=failure&amount=1.0&account_id=1	2025-11-28 02:34:35.066723	2025-11-28 02:34:35.261499	2025-11-28 02:49:35.066729
36	PSE-7638d8d6bf384f8ba0bc	100	1	1	COP	APPROVED	PSE	\N	\N		\N	http://13.217.221.47/pse_pse/resultado?status=success&amount=1.0&account_id=1	http://13.217.221.47/pse_pse/resultado?status=failure&amount=1.0&account_id=1	2025-11-28 02:42:59.190192	2025-11-28 02:42:59.39821	2025-11-28 02:57:59.1902
37	PSE-5b1c4317984a48b0b389	100	1	1210	COP	APPROVED	PSE	\N	\N		\N	http://13.217.221.47/pse_pse/resultado?status=success&amount=1210.0&account_id=1	http://13.217.221.47/pse_pse/resultado?status=failure&amount=1210.0&account_id=1	2025-11-28 02:47:22.940659	2025-11-28 02:47:23.218813	2025-11-28 03:02:22.940666
38	PSE-c32bf25af3674bf7b5ac	100	2	100	COP	APPROVED	PSE	\N	\N		\N	http://13.217.221.47/pse_pse/resultado?status=success&amount=100.0&account_id=2	http://13.217.221.47/pse_pse/resultado?status=failure&amount=100.0&account_id=2	2025-11-28 02:50:52.180499	2025-11-28 02:50:52.405117	2025-11-28 03:05:52.180506
39	PSE-8a70f6d23c55412d8e68	100	1	100	COP	REJECTED	PSE	\N	\N		\N	http://13.217.221.47/pse/resultado?status=success&amount=100.0&account_id=1	http://13.217.221.47/pse/resultado?status=failure&amount=100.0&account_id=1	2025-12-03 15:28:33.921204	2025-12-03 15:28:34.113053	2025-12-03 15:43:33.92121
40	PSE-ed9142cc41d14d628aca	100	1	100	COP	APPROVED	PSE	\N	\N		\N	http://13.217.221.47/pse/resultado?status=success&amount=100.0&account_id=1	http://13.217.221.47/pse/resultado?status=failure&amount=100.0&account_id=1	2025-12-03 15:29:01.67123	2025-12-03 15:29:01.867417	2025-12-03 15:44:01.671236
41	PSE-0a3cb059e85746b090be	101	3	100	COP	APPROVED	PSE	\N	\N		\N	http://13.217.221.47/pse/resultado?status=success&amount=100.0&account_id=3	http://13.217.221.47/pse/resultado?status=failure&amount=100.0&account_id=3	2025-12-04 02:55:01.637062	2025-12-04 02:55:01.849852	2025-12-04 03:10:01.637069
42	PSE-dadd370e71024da7af4e	100	1	11	COP	APPROVED	PSE	\N	\N		\N	http://13.217.221.47/pse_pse/resultado?status=success&amount=11.0&account_id=1	http://13.217.221.47/pse_pse/resultado?status=failure&amount=11.0&account_id=1	2025-12-04 02:56:53.745244	2025-12-04 02:56:53.945965	2025-12-04 03:11:53.74525
43	PSE-d3f844be26ac4f0eab54	100	1	10	COP	APPROVED	PSE	\N	\N		\N	http://44.221.46.147/pse/resultado?status=success&amount=10.0&account_id=1	http://44.221.46.147/pse/resultado?status=failure&amount=10.0&account_id=1	2026-02-08 19:56:18.581865	2026-02-08 19:56:18.786977	2026-02-08 20:11:18.581871
44	PSE-75bc50a5c53b4d8a918b	100	2	10	COP	APPROVED	PSE	\N	\N		\N	http://44.221.46.147/pse/resultado?status=success&amount=10.0&account_id=2	http://44.221.46.147/pse/resultado?status=failure&amount=10.0&account_id=2	2026-02-08 19:56:43.536433	2026-02-08 19:56:43.724615	2026-02-08 20:11:43.536439
45	PSE-5dd1a55aa60347108b50	101	3	58.99	COP	APPROVED	PSE	\N	\N		\N	http://44.221.46.147/pse/resultado?status=success&amount=58.99&account_id=3	http://44.221.46.147/pse/resultado?status=failure&amount=58.99&account_id=3	2026-02-08 19:58:24.426175	2026-02-08 19:58:24.618733	2026-02-08 20:13:24.426182
46	PSE-ed469a79eebd4befaff2	101	3	10	COP	APPROVED	PSE	\N	\N		\N	http://44.221.46.147/pse/resultado?status=success&amount=10.0&account_id=3	http://44.221.46.147/pse/resultado?status=failure&amount=10.0&account_id=3	2026-02-08 22:21:17.926189	2026-02-08 22:21:18.130016	2026-02-08 22:36:17.926195
47	PSE-70312306a17d4aaea8c5	100	1	10	COP	APPROVED	PSE	\N	\N		\N	http://44.221.46.147/pse_pse/resultado?status=success&amount=10.0&account_id=1	http://44.221.46.147/pse_pse/resultado?status=failure&amount=10.0&account_id=1	2026-02-08 22:22:35.964046	2026-02-08 22:22:36.148135	2026-02-08 22:37:35.964052
48	PSE-d393474793144da7b524	101	3	30	COP	REJECTED	PSE	\N	\N		\N	http://44.221.46.147/pse/resultado?status=success&amount=30.0&account_id=3	http://44.221.46.147/pse/resultado?status=failure&amount=30.0&account_id=3	2026-02-12 01:46:08.198097	2026-02-12 01:46:08.365147	2026-02-12 02:01:08.198104
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: banco_user
--

COPY public.users (id, username, hashed_password) FROM stdin;
1	admin	$pbkdf2-sha256$29000$PeccI4QwZgzhXGsN4by3tg$2IKFc.cBJeK1A5SSme/dvt527Ux8qIWM8FeyZTqcLJ4
2	user	$pbkdf2-sha256$29000$x9j7//8/JwQgZOwdg1BqzQ$sclPsb021If6vgkgFiLda6CiitHNVLvw.yKCdiwcIpE
\.


--
-- Data for Name: wallets; Type: TABLE DATA; Schema: public; Owner: banco_user
--

COPY public.wallets (id, customer_id, balance) FROM stdin;
1	100	300
2	101	50.5
\.


--
-- Name: accounts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: banco_user
--

SELECT pg_catalog.setval('public.accounts_id_seq', 1, false);


--
-- Name: movements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: banco_user
--

SELECT pg_catalog.setval('public.movements_id_seq', 30, true);


--
-- Name: pse_transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: banco_user
--

SELECT pg_catalog.setval('public.pse_transactions_id_seq', 48, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: banco_user
--

SELECT pg_catalog.setval('public.users_id_seq', 2, true);


--
-- Name: wallets_id_seq; Type: SEQUENCE SET; Schema: public; Owner: banco_user
--

SELECT pg_catalog.setval('public.wallets_id_seq', 1, false);


--
-- Name: accounts accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: banco_user
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_pkey PRIMARY KEY (id);


--
-- Name: movements movements_pkey; Type: CONSTRAINT; Schema: public; Owner: banco_user
--

ALTER TABLE ONLY public.movements
    ADD CONSTRAINT movements_pkey PRIMARY KEY (id);


--
-- Name: pse_transactions pse_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: banco_user
--

ALTER TABLE ONLY public.pse_transactions
    ADD CONSTRAINT pse_transactions_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: banco_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: wallets wallets_pkey; Type: CONSTRAINT; Schema: public; Owner: banco_user
--

ALTER TABLE ONLY public.wallets
    ADD CONSTRAINT wallets_pkey PRIMARY KEY (id);


--
-- Name: ix_accounts_customer_id; Type: INDEX; Schema: public; Owner: banco_user
--

CREATE INDEX ix_accounts_customer_id ON public.accounts USING btree (customer_id);


--
-- Name: ix_accounts_id; Type: INDEX; Schema: public; Owner: banco_user
--

CREATE INDEX ix_accounts_id ON public.accounts USING btree (id);


--
-- Name: ix_movements_customer_id; Type: INDEX; Schema: public; Owner: banco_user
--

CREATE INDEX ix_movements_customer_id ON public.movements USING btree (customer_id);


--
-- Name: ix_movements_id; Type: INDEX; Schema: public; Owner: banco_user
--

CREATE INDEX ix_movements_id ON public.movements USING btree (id);


--
-- Name: ix_pse_transactions_customer_id; Type: INDEX; Schema: public; Owner: banco_user
--

CREATE INDEX ix_pse_transactions_customer_id ON public.pse_transactions USING btree (customer_id);


--
-- Name: ix_pse_transactions_id; Type: INDEX; Schema: public; Owner: banco_user
--

CREATE INDEX ix_pse_transactions_id ON public.pse_transactions USING btree (id);


--
-- Name: ix_pse_transactions_internal_order_id; Type: INDEX; Schema: public; Owner: banco_user
--

CREATE UNIQUE INDEX ix_pse_transactions_internal_order_id ON public.pse_transactions USING btree (internal_order_id);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: banco_user
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: banco_user
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: ix_wallets_customer_id; Type: INDEX; Schema: public; Owner: banco_user
--

CREATE INDEX ix_wallets_customer_id ON public.wallets USING btree (customer_id);


--
-- Name: ix_wallets_id; Type: INDEX; Schema: public; Owner: banco_user
--

CREATE INDEX ix_wallets_id ON public.wallets USING btree (id);


--
-- Name: pse_transactions pse_transactions_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: banco_user
--

ALTER TABLE ONLY public.pse_transactions
    ADD CONSTRAINT pse_transactions_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.accounts(id);


--
-- PostgreSQL database dump complete
--

\unrestrict D2ildhNWoHP3jKg7hgDSfBnNiaxu34779XAnQz0clEcC9EFbDKZPhYF6Q4FjXFt

