"""Import datas"""
import csv
import datetime
import json
from datetime import datetime
import pymysql
import pandas as pd
import logging


logging.basicConfig(filename='project.log',
                    format='%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
                    level=logging.INFO)


def open_json(filename):
    """ Searches the file passed in argument and make sure it opens correctly and return his content as a dict"""
    try:
        with open(filename, 'r', encoding='utf-8') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        logging.critical(f"{filename} has not been found. No such file in this directory.")
        exit()


# CONSTANT
JSON_CONFIG = open_json('conf.json')


def data_distributor(nb_rows):
    """Record the distributors of movies"""
    distributor = []
    dd = []
    with open("data_scrapped.csv", "r", encoding='utf8') as my_file:
        reader = csv.DictReader(my_file)
        logging.info('reader OK in data_distributor()')
        dist_id = 1
        for j in reader:
            mydistributor = j['Distributor:']  # 1
            mydistributor = mydistributor.strip()
            if mydistributor not in dd:
                distributor.append((dist_id, mydistributor))  # TAB DISTRIBUTOR ID NAME
                logging.info('distributor list UPDATED in data_distributor()')
                dd.append(mydistributor)
                dist_id += 1
        logging.info('distributor OK in data_distributor()')
        return distributor


def my_date(d):
    """Check if the date d if correct otherwise it changes it to the right format"""
    date_dict = JSON_CONFIG['date_dict']
    try:
        dd = int(d[-4:])
        mm = date_dict[d[:3]]
        day = int(d[4:6])
        logging.info('date format OK in my_date()')
    except ValueError:
        dd = int(9999)
        mm = int(1)
        day = int(1)
        logging.info('adapted date format OK in my_date()')
    date = datetime(dd, mm, day)
    return date


def int_note(value):
    """ Check if value is an int otherwise return -1. It allows us to check if the movie has a grade or not"""
    try:
        res = int(value)
        logging.info('variables format OK in data_movies()')
    except ValueError:
        res = int(-1)
    return res


def data_movies(nb_rows, max_id):
    """Record the movies datas"""
    data = []
    with open("data_scrapped.csv", "r", encoding='utf-8') as my_file:
        reader = csv.DictReader(my_file)
        logging.info('reader OK in data_movies()')
        movie_id = max_id + 1
        dist_id = 1
        for j in reader:
            title = j['Title']  # 1
            tomatometer = j['Tomatometer']  # 1
            metascore = j['Metascore']
            original_language = j['Original Language:'].strip()  # 1
            d = j['Release Date (Theaters):']
            rating = j['Rating:']
            date = my_date(d)
            tomatometer = int_note(tomatometer)
            metascore = int_note(metascore)
            data.append((int(movie_id), str(title), int(tomatometer), int(metascore), date,
                         str(original_language).strip(), str(rating).strip(), int(dist_id)))
            movie_id += 1
    logging.info('datas OK in data_movies()')
    return data


def data_cast(nb_rows):
    """Record the cast of the movie"""
    actor = {}
    actors = []
    cast_id = 1
    act_id = 1
    my_cast = []
    movie_id = 1
    with open("data_scrapped.csv", "r", encoding='utf-8') as my_file:
        reader = csv.DictReader(my_file)
        logging.info('reader OK in data_cast()')
        movie_id = 1
        for j in reader:
            cast = j['cast']  # MANY
            cast2 = cast.replace('[', ',')
            cast2 = cast2.replace(']', ',')
            cast2 = cast2.replace('"', ',')
            cast2 = cast2.split(',')
            for act in cast2:
                if act not in actors:
                    actors.append((int(act_id), str(act)))  # TAB ACTORS NAME ID
                    actor[act] = act_id
                    act_id += 1
                    my_cast.append((cast_id, movie_id, actor[act]))  # TAB CAST ID M_ID A_ID
                    cast_id += 1
                    logging.info('new actor added OK in data_cast()')
                else:
                    my_cast.append((cast_id, movie_id, actor[act]))  # TAB CAST ID M_ID A_ID
                    cast_id += 1
                    logging.info('existed actor add to cast table OK in data_cast()')
            movie_id += 1
    logging.info('cast OK in data_cast()')
    return my_cast, actors


def data_genre(nb_rows):
    """Record the genre of movies"""
    genre = []
    my_g = []
    genre_id = 1
    gom_id = 1
    genress = {}
    genre_of_movie = []
    with open("data_scrapped.csv", "r", encoding='utf-8') as my_file:
        reader = csv.DictReader(my_file)
        logging.info('reader OK in data_genre()')
        movie_id = 1
        for j in reader:
            ggenre = j['Genre:']
            my_genre = ggenre.split(', ')
            for g in my_genre:
                my_gg = g.strip()
                if my_gg not in my_g:
                    genre.append((genre_id, my_gg))
                    my_g.append(my_gg)
                    genress[my_gg] = genre_id
                    genre_of_movie.append((gom_id, movie_id, genress[my_gg]))
                    genre_id += 1
                    gom_id += 1
                    logging.info('new genre added OK in data_genre()')
                else:
                    genress[g] = genress[my_gg]
                    genre_of_movie.append((gom_id, movie_id, genress[my_gg]))
                    gom_id += 1
                    logging.info('existed genre added to genre of movies OK in data_genre()')
            movie_id += 1
    return genre, genre_of_movie


def data_movie_staff(nb_rows):
    """Record the staff of movies"""
    movie_staff = []
    movies_staff = {}
    staff = []
    ms_id = 1
    staff_id = 1
    movie_id = 1
    with open("data_scrapped.csv", "r", encoding='utf-8') as my_file:
        reader = csv.DictReader(my_file)
        logging.info('reader OK in data_movie_staff()')
        movie_id = 1
        for j in reader:
            ddirector = j['Director:']
            pproducer = j['Producer:']
            wwriter = j['Writer:']
            my_dir = ddirector.split(', ')
            my_prod = pproducer.split(', ')
            my_wr = wwriter.split(', ')
            for dir in my_dir:
                if dir not in movie_staff:
                    movies_staff[dir] = ms_id
                    movie_staff.append((ms_id, dir))
                    ms_id += 1
                    staff.append(
                        (staff_id, movie_id, movies_staff[dir], 'Director'))
                    staff_id += 1
                    logging.info('new director added OK in data_movie_staff()')
            for prod in my_prod:
                if prod not in movie_staff:
                    movies_staff[prod] = ms_id
                    movie_staff.append((ms_id, prod))
                    ms_id += 1
                    staff.append((staff_id, movie_id, movies_staff[prod], 'Producer'))
                    staff_id += 1
                    logging.info('new producer added OK in data_movie_staff()')
            for wr in my_wr:
                if wr not in movie_staff:
                    movies_staff[wr] = ms_id
                    movie_staff.append((ms_id, wr))
                    ms_id += 1
                    staff.append((staff_id, movie_id, movies_staff[wr], 'Writer'))
                    staff_id += 1
                    logging.info('new writer added OK in data_movie_staff()')
            movie_id += 1
    return movie_staff, staff


def data(nb_rows, max_id):
    """ Call the differents functions that convert the csv file to different infos variables about the movie."""
    distributor = data_distributor(nb_rows)
    logging.info('data_distributor called successfully')
    data = data_movies(nb_rows, max_id)
    logging.info('data_movies called successfully')
    my_cast, actors = data_cast(nb_rows)
    logging.info('data_cast called successfully')
    genre, genre_of_movie = data_genre(nb_rows)
    logging.info('data_genre called successfully')
    movie_staff, staff = data_movie_staff(nb_rows)
    logging.info('data_movie_staff called successfully')
    return data, distributor, actors, my_cast, genre, genre_of_movie, movie_staff, staff


# TAB DATA:  movie_id, Title, Tomatometer, Genre, Original_Language,
# Director, Producer, Writer, Box_Office, cast, Distributor
# TAB DISTRIBUTOR: ID NAME
# TAB ACTORS: ID NAME
# TAB CAST: ID M_ID A_ID
# TAB GENRE ID GENRE
# TAB GENRE OF MOVIE ID M_ID G_ID
# TAB MOVIE STAFF: ID NAME
# TAB STAFF OF MOVIE: ID M_ID S_ID Job

def aesthetic_print():
    """
    Print a fancy logo for the command line
    """
    print('********************************************************************************************')
    print('********************************************************************************************')
    print('****                                                                                    ****')
    print('****                                 DATA ANALYZED                                      ****')
    print('****                                                                                    ****')
    print('********************************************************************************************')
    print('********************************************************************************************')


def creation_db():
    """
    Create the database
    """
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='root',
                                 cursorclass=pymysql.cursors.Cursor)
    with connection:
        with connection.cursor() as my_cursor:
            sql = "CREATE DATABASE rt_project;"
            my_cursor.execute(sql)
        connection.commit()
    logging.info('database created successfully')


def connect_db():
    """
    Connect to db
    """
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='root',
                                 database='rt_project',
                                 cursorclass=pymysql.cursors.Cursor)
    logging.info('database connected successfully')
    return connection


def query_db1(my_query):
    """
    Allow to query the database with my_query
    """
    connection = connect_db()
    with connection:
        with connection.cursor() as my_cursor:
            sql = my_query
            my_cursor.execute(sql)
            result = my_cursor.fetchall()
        connection.commit()
    logging.info('query_db1 used successfully')
    return result


def query_db(my_query, data):
    """
    Allow to query the database multiple times
    """
    connection = connect_db()
    with connection:
        with connection.cursor() as my_cursor:
            sql = my_query
            datas = data
            my_cursor.execute(sql, datas)
            result = my_cursor.fetchall()
        connection.commit()
    logging.info('query_db used successfully')
    return result


def exist():
    """
    Find and return the maximum id if it exists and return 0 otherwise
    """
    a = query_db1(JSON_CONFIG['QEXIST'])
    max_id = query_db1(JSON_CONFIG['QMAXEXIST'])[0][0]
    if max_id is None:
        logging.info('max_id was not founded --> 0')
        max_id = 0
    else:
        logging.info(f'max_id was founded --> {max_id}')
        pass
    logging.info('exist() used successfully')
    return a, max_id


def clean_empty():
    """
    Delete all wrong lines with missing values
    """
    query_db1(JSON_CONFIG['QEMOVIES'])
    query_db1(JSON_CONFIG['QEDISTRIBUTORS'])
    query_db1(JSON_CONFIG['QEACTORS'])
    query_db1(JSON_CONFIG['QEGOM'])
    query_db1(JSON_CONFIG['QESOM'])
    query_db1(JSON_CONFIG['QEGENRES'])
    query_db1(JSON_CONFIG['QECAST'])
    logging.info('All the empty lines removed')


def my_movies():
    """
    Create the table movies in the database
    """
    try:
        query_db1(JSON_CONFIG['QMYMOVIES'])
        logging.info('movies table created')
    except pymysql.err.OperationalError:
        logging.info('movies table already exist')
        pass


def db_movies(nb_rows):
    """Fill the columns per table (8) per 100 lines batches:
    movies, actors, distributor, cast, staff_of_movie, movie_staff, genre_of_movie, genres
    """
    my_movies()
    e = exist()
    a = e[0]
    list_m = []
    list_mm = query_db1(JSON_CONFIG['QDMOVIESTITLE'])
    for m in list_mm:
        list_m.append(m[0])
    logging.info('list of movies defined successfully')
    max_id = e[1]
    datas = data(nb_rows, max_id)
    movie_info = datas[0]
    cpt = 0
    while cpt <= nb_rows - 1:
        if movie_info[cpt][1] not in list_m:
            try:
                query_db(JSON_CONFIG['QDBMOVIES'], movie_info[cpt])
                logging.info('movies added successfully')
            except pymysql.err.IntegrityError:
                logging.info('movies already exist')
                pass
        cpt += 1


def my_actors():
    """
    Create table actors in the database if it doesn't exist
    """
    try:
        query_db1(JSON_CONFIG['QMYACTOR'])
        logging.info('actors table added successfully')
    except pymysql.err.OperationalError:
        logging.info('actors table already exists')
        pass


def db_actors(nb_rows):
    """
    Insert the datas about actors into the table actors
    """
    my_actors()
    e = exist()
    max_id = e[1]
    datas = data(nb_rows, max_id)
    cpt = 0
    cpt_id = 1
    actors = datas[2]
    while cpt <= len(actors)-1:
        try:
            query_db(JSON_CONFIG['QDBACTORS'], actors[cpt])
            logging.info('actors added successfully')
        except pymysql.err.IntegrityError:
            logging.info('actors already exists')
            pass
        cpt_id += 1
        cpt += 1


def my_distributors():
    """
    Create the table distributors if it doesn't exist
    """
    try:
        query_db1(JSON_CONFIG['QMYDISTRIBUTORS'])
        logging.info('my_distributor table added successfully')
    except pymysql.err.OperationalError:
        logging.info('my_distributor table already exists')
        pass


def db_distributors(nb_rows):
    """
    Insert the datas about distributors into the table distributors
    """
    my_distributors()
    e = exist()
    a = e[0]
    max_id = e[1]
    datas = data(nb_rows, max_id)
    cpt = 0
    cpt_id = 1
    distributors = datas[1]
    while cpt <= len(distributors)-1:
        try:
            query_db(JSON_CONFIG['QDBDISYTIBUTORS'], distributors[cpt])
            logging.info('distributor added successfully')
        except pymysql.err.IntegrityError:
            logging.info('distributor already exists')
            pass
        cpt_id += 1
        cpt += 1


def my_cast():
    """
    Create the table cast if it doesn't exist
    """
    try:
        query_db1(JSON_CONFIG['QMYCAST'])
        logging.info('my_cast table added successfully')
    except pymysql.err.OperationalError:
        logging.info('my_cast table already exists')
        pass


def db_cast(nb_rows):
    """
    Insert the datas about cast into the table cast
    """
    my_cast()
    e = exist()
    max_id = e[1]
    datas = data(nb_rows, max_id)
    cpt = 0
    cpt_id = 1
    cast = datas[3]
    while cpt <= len(cast)-1:
        try:
            query_db(JSON_CONFIG['QDBCAST'], cast[cpt])
            logging.info('new cast added successfully')
        except pymysql.err.IntegrityError:
            logging.info('cast already exists')
            pass
        cpt_id += 1
        cpt += 1


def my_genre():
    """
    Create the table genre if it doesn't exist
    """
    try:
        query_db1(JSON_CONFIG['QMYGENRE'])
        logging.info('genre table added successfully')
    except pymysql.err.OperationalError:
        logging.info('genre table already exists')
        pass


def db_genre(nb_rows):
    """
    Insert the datas about genre into the table genre
    """
    my_genre()
    e = exist()
    max_id = e[1]
    datas = data(nb_rows, max_id)
    cpt = 0
    cpt_id = 1
    genres = datas[4]
    while cpt <= len(genres) - 1:
        try:
            query_db(JSON_CONFIG['QDGGENRE'], genres[cpt])
            logging.info('new genre added successfully')
        except pymysql.err.IntegrityError:
            logging.info('genre already exists')
            pass
        cpt_id += 1
        cpt += 1


def my_gom():
    """
    Create the table genre of movie if it doesn't exist
    """
    try:
        query_db1(JSON_CONFIG['QMYGOM'])
        logging.info('my_gom table added successfully')
    except pymysql.err.OperationalError:
        logging.info('my_gom table already exists')
        pass


def db_gom(nb_rows):
    """
    Insert the datas about genre of movies into the table genre_of_movie
    """
    my_gom()
    e = exist()
    max_id = e[1]
    datas = data(nb_rows, max_id)
    cpt = 0
    cpt_id = 1
    gom = datas[5]
    while cpt <= len(gom) - 1:
        try:
            query_db(JSON_CONFIG['QDBGOM'], gom[cpt])
            logging.info('new genre of movie added successfully')
        except pymysql.err.IntegrityError:
            logging.info('genre of movie already exists')
            pass
        cpt_id += 1
        cpt += 1


def my_staff():
    """
    Create the table staff if it doesn't exist
    """
    try:
        query_db1(JSON_CONFIG['QMYSTAFF'])
        logging.info('my_staff table added successfully')
    except pymysql.err.OperationalError:
        logging.info('my_staff table already exists')
        pass


def db_staff(nb_rows):
    """
    Insert the datas about staffs into the table staff
    """
    my_staff()
    e = exist()
    max_id = e[1]
    datas = data(nb_rows, max_id)
    cpt = 0
    cpt_id = 1
    ms = datas[6]
    while cpt <= len(ms) - 1:
        try:
            query_db(JSON_CONFIG['QDBSTAFF'], ms[cpt])
            logging.info('new staff added successfully')
        except pymysql.err.IntegrityError:
            logging.info('staff already exists')
            pass
        cpt_id += 1
        cpt += 1


def my_sof():
    """
    Create the table staff_of_movie if it doesn't exist
    """
    try:
        query_db1(JSON_CONFIG['QMYSOF'])
        logging.info('staff of movie table added successfully')
    except pymysql.err.OperationalError:
        logging.info('staff of movie table already exists')
        pass


def db_staff_of_movie(nb_rows):
    """
    Insert the datas about staff of movies into the table staff_of_movie
    """
    my_sof()
    e = exist()
    max_id = e[1]
    datas = data(nb_rows, max_id)
    cpt = 0
    cpt_id = 1
    ms = datas[7]
    while cpt <= len(ms) - 1:
        try:
            query_db(JSON_CONFIG['QDBSOF'], ms[cpt])
            logging.info('staff of movie added successfully')
        except pymysql.err.IntegrityError:
            logging.info('staff of movie already exists')
            pass
        cpt_id += 1
        cpt += 1


def create_db():
    """
    Create the database if it doesn't exist
    """
    try:
        creation_db()
        print('CREATION DB')
        logging.info('DataBase created successfully')
    except pymysql.err.ProgrammingError:
        print('CREATION DB ALREADY DONE')
        logging.info('DataBase already exists')


def application():
    """Call all the functions that create and insert data in the database"""
    aesthetic_print()
    nb_rows = len(pd.read_csv('data_scrapped.csv'))
    logging.info('nb_rows detected')
    create_db()
    logging.info('DataBase created successfully in application()')
    db_movies(nb_rows)
    print('FILL MOVIES --> DONE')
    logging.info('movies table filled successfully')
    db_actors(nb_rows)
    print('FILL ACTORS --> DONE')
    logging.info('actors table filled successfully')
    db_distributors(nb_rows)
    print('FILL DISTRIBUTORS --> DONE')
    logging.info('distributor table filled successfully')
    db_cast(nb_rows)
    print('FILL CAST --> DONE')
    logging.info('cast table filled successfully')
    db_genre(nb_rows)
    print('FILL GENRES --> DONE')
    logging.info('genre table filled successfully')
    db_gom(nb_rows)
    print('FILL GENRE OF MOVIES --> DONE')
    logging.info('genre of movies table filled successfully')
    db_staff(nb_rows)
    print('FILL STAFF --> DONE')
    logging.info('staff table filled successfully')
    db_staff_of_movie(nb_rows)
    print('FILL STAFF OF MOVIES --> DONE')
    logging.info('staff of movies table filled successfully')
    clean_empty()
    print('CLEAN EMPTY LINES --> DONE')
    logging.info('empty lines removed successfully')
    print('****************** THE END ******************')
