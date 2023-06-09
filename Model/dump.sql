PGDMP                         {            MailAnalyze    15.0    15.0 1    n
           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            o
           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            p
           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            q
           1262    16436    MailAnalyze    DATABASE     �   CREATE DATABASE "MailAnalyze" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'Russian_Russia.1251';
    DROP DATABASE "MailAnalyze";
                postgres    false                        3079    16501    pg_trgm 	   EXTENSION     ;   CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;
    DROP EXTENSION pg_trgm;
                   false            r
           0    0    EXTENSION pg_trgm    COMMENT     e   COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';
                        false    2            D           3602    16500    russian_multilingual    TEXT SEARCH CONFIGURATION       CREATE TEXT SEARCH CONFIGURATION public.russian_multilingual (
    PARSER = pg_catalog."default" );

ALTER TEXT SEARCH CONFIGURATION public.russian_multilingual
    ADD MAPPING FOR asciiword WITH english_stem;

ALTER TEXT SEARCH CONFIGURATION public.russian_multilingual
    ADD MAPPING FOR word WITH english_stem;

ALTER TEXT SEARCH CONFIGURATION public.russian_multilingual
    ADD MAPPING FOR numword WITH simple;

ALTER TEXT SEARCH CONFIGURATION public.russian_multilingual
    ADD MAPPING FOR email WITH simple;

ALTER TEXT SEARCH CONFIGURATION public.russian_multilingual
    ADD MAPPING FOR url WITH simple;

ALTER TEXT SEARCH CONFIGURATION public.russian_multilingual
    ADD MAPPING FOR host WITH simple;

ALTER TEXT SEARCH CONFIGURATION public.russian_multilingual
    ADD MAPPING FOR sfloat WITH simple;

ALTER TEXT SEARCH CONFIGURATION public.russian_multilingual
    ADD MAPPING FOR version WITH simple;

ALTER TEXT SEARCH CONFIGURATION public.russian_multilingual
    ADD MAPPING FOR hword_numpart WITH simple;

ALTER TEXT SEARCH CONFIGURATION public.russian_multilingual
    ADD MAPPING FOR hword_part WITH english_stem;

ALTER TEXT SEARCH CONFIGURATION public.russian_multilingual
    ADD MAPPING FOR hword_asciipart WITH english_stem;

ALTER TEXT SEARCH CONFIGURATION public.russian_multilingual
    ADD MAPPING FOR numhword WITH simple;

ALTER TEXT SEARCH CONFIGURATION public.russian_multilingual
    ADD MAPPING FOR asciihword WITH english_stem;

ALTER TEXT SEARCH CONFIGURATION public.russian_multilingual
    ADD MAPPING FOR hword WITH english_stem;

ALTER TEXT SEARCH CONFIGURATION public.russian_multilingual
    ADD MAPPING FOR url_path WITH simple;

ALTER TEXT SEARCH CONFIGURATION public.russian_multilingual
    ADD MAPPING FOR file WITH simple;

ALTER TEXT SEARCH CONFIGURATION public.russian_multilingual
    ADD MAPPING FOR "float" WITH simple;

ALTER TEXT SEARCH CONFIGURATION public.russian_multilingual
    ADD MAPPING FOR "int" WITH simple;

ALTER TEXT SEARCH CONFIGURATION public.russian_multilingual
    ADD MAPPING FOR uint WITH simple;
 <   DROP TEXT SEARCH CONFIGURATION public.russian_multilingual;
       public          postgres    false            �            1259    16790 	   companies    TABLE     j   CREATE TABLE public.companies (
    id bigint NOT NULL,
    name text NOT NULL,
    type text NOT NULL
);
    DROP TABLE public.companies;
       public         heap    postgres    false            s
           0    0    TABLE companies    COMMENT     W   COMMENT ON TABLE public.companies IS 'содержит список компаний';
          public          postgres    false    223            �            1259    16789    Companies_id_seq    SEQUENCE     �   ALTER TABLE public.companies ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public."Companies_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    223            �            1259    16777    domains    TABLE     r   CREATE TABLE public.domains (
    id bigint NOT NULL,
    domain text NOT NULL,
    company_id bigint NOT NULL
);
    DROP TABLE public.domains;
       public         heap    postgres    false            �            1259    16776    Domains_id_seq    SEQUENCE     �   ALTER TABLE public.domains ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public."Domains_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    221            �            1259    16599    email_addresses    TABLE     j   CREATE TABLE public.email_addresses (
    id bigint NOT NULL,
    address text NOT NULL,
    name text
);
 #   DROP TABLE public.email_addresses;
       public         heap    postgres    false            �            1259    16598    Email_Adresses_id_seq    SEQUENCE     �   ALTER TABLE public.email_addresses ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public."Email_Adresses_id_seq"
    START WITH 0
    INCREMENT BY 1
    MINVALUE 0
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    219            �            1259    16591 	   recievers    TABLE     �   CREATE TABLE public.recievers (
    id bigint NOT NULL,
    message_id text NOT NULL,
    address_id bigint NOT NULL,
    type character varying(15)
);
    DROP TABLE public.recievers;
       public         heap    postgres    false            �            1259    16590    Senders_Recievers_id_seq    SEQUENCE     �   ALTER TABLE public.recievers ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public."Senders_Recievers_id_seq"
    START WITH 0
    INCREMENT BY 1
    MINVALUE 0
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    217            �            1259    17069    files    TABLE     �   CREATE TABLE public.files (
    id bigint NOT NULL,
    name text NOT NULL,
    text text,
    bytes bytea,
    message_id text NOT NULL
);
    DROP TABLE public.files;
       public         heap    postgres    false            �            1259    17150    files_id_seq    SEQUENCE     �   ALTER TABLE public.files ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.files_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    224            �            1259    16583    messages    TABLE     �   CREATE TABLE public.messages (
    id text NOT NULL,
    subject text,
    sender_id bigint,
    datetime timestamp with time zone NOT NULL,
    priority text,
    body text,
    reply_id text
);
    DROP TABLE public.messages;
       public         heap    postgres    false            �            1259    27031    v_companies_domains    VIEW       CREATE VIEW public.v_companies_domains AS
 SELECT cm.id AS company_id,
    cm.name AS company_name,
    cm.type AS company_type,
    dm.id AS domain_id,
    dm.domain
   FROM (public.companies cm
     LEFT JOIN public.domains dm ON ((dm.company_id = cm.id)));
 &   DROP VIEW public.v_companies_domains;
       public          postgres    false    221    221    223    223    223    221            �            1259    27035    v_mails_info    VIEW     �  CREATE VIEW public.v_mails_info AS
 SELECT msg.id,
    msg.reply_id,
    msg.subject,
    msg.datetime,
    msg.priority,
    msg.body,
    ea1.address AS sender_address,
    ea1.name AS sender_name,
    vcd1.company_name AS sender_company_name,
    vcd1.company_type AS sender_company_type,
    ea2.address AS reciever_address,
    ea2.name AS reciever_name,
    rcv.type AS reciever_type,
    vcd2.company_name AS reciever_company_name,
    vcd2.company_type AS reciever_company_type
   FROM (((((public.messages msg
     LEFT JOIN public.email_addresses ea1 ON ((msg.sender_id = ea1.id)))
     LEFT JOIN public.recievers rcv ON ((msg.id = rcv.message_id)))
     LEFT JOIN public.email_addresses ea2 ON ((rcv.address_id = ea2.id)))
     LEFT JOIN public.v_companies_domains vcd1 ON (("substring"(ea1.address, '@(.*)'::text) = vcd1.domain)))
     LEFT JOIN public.v_companies_domains vcd2 ON (("substring"(ea2.address, '@(.*)'::text) = vcd2.domain)));
    DROP VIEW public.v_mails_info;
       public          postgres    false    215    215    217    217    217    219    219    215    215    215    215    215    219    226    226    226            i
          0    16790 	   companies 
   TABLE DATA           3   COPY public.companies (id, name, type) FROM stdin;
    public          postgres    false    223   �B       g
          0    16777    domains 
   TABLE DATA           9   COPY public.domains (id, domain, company_id) FROM stdin;
    public          postgres    false    221   C       e
          0    16599    email_addresses 
   TABLE DATA           <   COPY public.email_addresses (id, address, name) FROM stdin;
    public          postgres    false    219   2C       j
          0    17069    files 
   TABLE DATA           B   COPY public.files (id, name, text, bytes, message_id) FROM stdin;
    public          postgres    false    224   OC       a
          0    16583    messages 
   TABLE DATA           ^   COPY public.messages (id, subject, sender_id, datetime, priority, body, reply_id) FROM stdin;
    public          postgres    false    215   lC       c
          0    16591 	   recievers 
   TABLE DATA           E   COPY public.recievers (id, message_id, address_id, type) FROM stdin;
    public          postgres    false    217   �C       t
           0    0    Companies_id_seq    SEQUENCE SET     A   SELECT pg_catalog.setval('public."Companies_id_seq"', 1, false);
          public          postgres    false    222            u
           0    0    Domains_id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('public."Domains_id_seq"', 1, false);
          public          postgres    false    220            v
           0    0    Email_Adresses_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public."Email_Adresses_id_seq"', 0, false);
          public          postgres    false    218            w
           0    0    Senders_Recievers_id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public."Senders_Recievers_id_seq"', 0, false);
          public          postgres    false    216            x
           0    0    files_id_seq    SEQUENCE SET     ;   SELECT pg_catalog.setval('public.files_id_seq', 1, false);
          public          postgres    false    225            �           2606    16796    companies Companies_pkey 
   CONSTRAINT     X   ALTER TABLE ONLY public.companies
    ADD CONSTRAINT "Companies_pkey" PRIMARY KEY (id);
 D   ALTER TABLE ONLY public.companies DROP CONSTRAINT "Companies_pkey";
       public            postgres    false    223            �           2606    16783    domains Domains_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.domains
    ADD CONSTRAINT "Domains_pkey" PRIMARY KEY (id);
 @   ALTER TABLE ONLY public.domains DROP CONSTRAINT "Domains_pkey";
       public            postgres    false    221            �           2606    16605 #   email_addresses Email_Adresses_pkey 
   CONSTRAINT     c   ALTER TABLE ONLY public.email_addresses
    ADD CONSTRAINT "Email_Adresses_pkey" PRIMARY KEY (id);
 O   ALTER TABLE ONLY public.email_addresses DROP CONSTRAINT "Email_Adresses_pkey";
       public            postgres    false    219            �           2606    17075    files FIles_pkey 
   CONSTRAINT     P   ALTER TABLE ONLY public.files
    ADD CONSTRAINT "FIles_pkey" PRIMARY KEY (id);
 <   ALTER TABLE ONLY public.files DROP CONSTRAINT "FIles_pkey";
       public            postgres    false    224            �           2606    16589    messages Messages_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY public.messages
    ADD CONSTRAINT "Messages_pkey" PRIMARY KEY (id);
 B   ALTER TABLE ONLY public.messages DROP CONSTRAINT "Messages_pkey";
       public            postgres    false    215            �           2606    16597     recievers Senders_Recievers_pkey 
   CONSTRAINT     `   ALTER TABLE ONLY public.recievers
    ADD CONSTRAINT "Senders_Recievers_pkey" PRIMARY KEY (id);
 L   ALTER TABLE ONLY public.recievers DROP CONSTRAINT "Senders_Recievers_pkey";
       public            postgres    false    217            �           2606    17149    domains domain_unique 
   CONSTRAINT     ^   ALTER TABLE ONLY public.domains
    ADD CONSTRAINT domain_unique UNIQUE (domain, company_id);
 ?   ALTER TABLE ONLY public.domains DROP CONSTRAINT domain_unique;
       public            postgres    false    221    221            �           2606    17147    companies name_unique 
   CONSTRAINT     P   ALTER TABLE ONLY public.companies
    ADD CONSTRAINT name_unique UNIQUE (name);
 ?   ALTER TABLE ONLY public.companies DROP CONSTRAINT name_unique;
       public            postgres    false    223            �           2606    16625    email_addresses unique_address 
   CONSTRAINT     \   ALTER TABLE ONLY public.email_addresses
    ADD CONSTRAINT unique_address UNIQUE (address);
 H   ALTER TABLE ONLY public.email_addresses DROP CONSTRAINT unique_address;
       public            postgres    false    219            �           1259    16837    body_idx    INDEX     ^   CREATE INDEX body_idx ON public.messages USING gin (to_tsvector('russian'::regconfig, body));
    DROP INDEX public.body_idx;
       public            postgres    false    215    215            �           1259    27040    files_text_idx    INDEX     a   CREATE INDEX files_text_idx ON public.files USING gin (to_tsvector('russian'::regconfig, text));
 "   DROP INDEX public.files_text_idx;
       public            postgres    false    224    224            �           1259    16838    subject_idx    INDEX     d   CREATE INDEX subject_idx ON public.messages USING gin (to_tsvector('russian'::regconfig, subject));
    DROP INDEX public.subject_idx;
       public            postgres    false    215    215            �           2606    17064    recievers adress_id_FK 
   FK CONSTRAINT     �   ALTER TABLE ONLY public.recievers
    ADD CONSTRAINT "adress_id_FK" FOREIGN KEY (address_id) REFERENCES public.email_addresses(id) ON UPDATE CASCADE ON DELETE CASCADE;
 B   ALTER TABLE ONLY public.recievers DROP CONSTRAINT "adress_id_FK";
       public          postgres    false    217    219    3262            �           2606    16932    domains company_id_FK 
   FK CONSTRAINT     �   ALTER TABLE ONLY public.domains
    ADD CONSTRAINT "company_id_FK" FOREIGN KEY (company_id) REFERENCES public.companies(id) ON UPDATE CASCADE ON DELETE CASCADE;
 A   ALTER TABLE ONLY public.domains DROP CONSTRAINT "company_id_FK";
       public          postgres    false    221    3270    223            �           2606    17007    recievers message_id_FK 
   FK CONSTRAINT     �   ALTER TABLE ONLY public.recievers
    ADD CONSTRAINT "message_id_FK" FOREIGN KEY (message_id) REFERENCES public.messages(id) ON UPDATE CASCADE ON DELETE CASCADE;
 C   ALTER TABLE ONLY public.recievers DROP CONSTRAINT "message_id_FK";
       public          postgres    false    217    215    3256            �           2606    17076    files message_id_FK 
   FK CONSTRAINT     �   ALTER TABLE ONLY public.files
    ADD CONSTRAINT "message_id_FK" FOREIGN KEY (message_id) REFERENCES public.messages(id) ON UPDATE CASCADE ON DELETE CASCADE NOT VALID;
 ?   ALTER TABLE ONLY public.files DROP CONSTRAINT "message_id_FK";
       public          postgres    false    215    3256    224            �           2606    16927    messages sender_id_FK 
   FK CONSTRAINT     �   ALTER TABLE ONLY public.messages
    ADD CONSTRAINT "sender_id_FK" FOREIGN KEY (sender_id) REFERENCES public.email_addresses(id) ON UPDATE CASCADE ON DELETE CASCADE;
 A   ALTER TABLE ONLY public.messages DROP CONSTRAINT "sender_id_FK";
       public          postgres    false    219    3262    215            i
   
   x������ � �      g
   
   x������ � �      e
   
   x������ � �      j
   
   x������ � �      a
   
   x������ � �      c
   
   x������ � �     