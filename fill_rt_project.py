"""## Import datas"""
import csv
import datetime
import tqdm
from tqdm import tqdm
from datetime import datetime
import pymysql
import pandas as pd


def data(nb_rows):
    """Datas configuration"""
    data = []
    actors = []
    actor = {}
    distributor = []
    disti = []
    distri = []
    d = {}
    my_cast = []
    genre = []
    genress = {}
    genre_of_movie = []
    movie_staff = []
    movies_staff = {}
    staff = []
    dist_id = 1
    Tomatometer = 0
    movie_id = 1
    act_id = 1
    cast_id = 1
    genre_id = 1
    gom_id = 1
    ms_id = 1
    staff_id = 1
    date_dict = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12
    }

    with open("data_scrapped.csv", "r") as my_file:
        reader = csv.DictReader(my_file)

        for j in tqdm(reader, total=nb_rows):
            Title = j['Title']  # 1
            Tomatometer = j['Tomatometer']  # 1
            Genre = j['Genre:']  # MANY
            Original_Language = j['Original Language:'].strip()  # 1
            Director = j['Director:']  # MANY
            Producer = j['Producer:']  # MANY
            d = j['Release Date (Theaters):']
            Rating = j['Rating:']
            try:
                dd = int(d[-4:])
                mm = date_dict[d[:3]]
                day = int(d[4:6])
            except ValueError:
                dd = int(9999)
                mm = int(1)
                day = int(1)
            Date = datetime(dd, mm, day)
            Writer = j['Writer:']  # MANY
            cast = j['cast']  # MANY
            Distributor = j['Distributor:']  # 1

            # Distributor
            for dist in Distributor.split(','):
                if dist not in distributor:
                    disti.append(dist.strip())
                    distributor.append((dist_id, dist))  # TAB DISTRIBUTOR ID NAME

            # Movies
            try:
                int(movie_id)
                int(Tomatometer)
            except ValueError:
                Tomatometer = int(-1)
            data.append((int(movie_id),
                         str(Title),
                         int(Tomatometer),
                         Date,
                         str(Original_Language).strip(),
                         str(Rating).strip(),
                         int(dist_id)))
            # TAB MOVIES

            # Actors, Cast
            cast2 = cast.split(',')
            for act in cast2:
                if act not in actor:
                    actors.append((int(act_id), str(act)))  # TAB ACTORS NAME ID
                    actor[act] = act_id
                    act_id += 1
                    my_cast.append((cast_id, movie_id, actor[act]))  # TAB CAST ID M_ID A_ID
                    cast_id += 1
                else:
                    my_cast.append((cast_id, movie_id, actor[act]))  # TAB CAST ID M_ID A_ID
                    cast_id += 1

            # Genre
            my_genre = Genre.split(', ')
            for g in my_genre:
                if g not in genre:  # add genre id
                    genre.append((genre_id, g.strip()))  # TAB GENRES
                    genress[g] = genre_id
                    genre_of_movie.append((gom_id, movie_id, genress[g]))  # TAB GENRE OF MOVIE ID M_ID GENRE
                    genre_id += 1
                    gom_id += 1
                else:
                    genre_of_movie.append((gom_id, movie_id, genre_id))  # TAB GENRE OF MOVIE ID M_ID GENRE
                    gom_id += 1

            # Movie Staff
            my_dir = Director.split(', ')
            my_prod = Producer.split(', ')
            my_wr = Writer.split(', ')
            for dir in my_dir:
                if dir not in movie_staff:
                    movies_staff[dir] = ms_id  # TAB MOVIE STAFF: ID NAME
                    movie_staff.append((ms_id, dir))  # TAB MOVIE STAFF: ID NAME
                    ms_id += 1
                    staff.append(
                        (staff_id, movie_id, movies_staff[dir], 'Director'))  # TAB STAFF OF MOVIE: ID M_ID S_ID Job
                    staff_id += 1
            for prod in my_prod:
                if prod not in movie_staff:
                    movies_staff[prod] = ms_id
                    movie_staff.append((ms_id, prod))
                    ms_id += 1
                    staff.append((staff_id, movie_id, movies_staff[prod], 'Producer'))
                    staff_id += 1
            for wr in my_wr:
                if wr not in movie_staff:
                    movies_staff[wr] = ms_id
                    movie_staff.append((ms_id, wr))
                    ms_id += 1
                    staff.append((staff_id, movie_id, movies_staff[wr], 'Writer'))
                    staff_id += 1

            movie_id += 1
            dist_id += 1

    return data, distributor, actors, my_cast, genre, genre_of_movie, movie_staff, staff


# TAB DATA:  movie_id, Title, Tomatometer, Genre, Original_Language, Director, Producer, Writer, Box_Office, cast, Distributor
# TAB DISTRIBUTOR: ID NAME
# TAB ACTORS: ID NAME
# TAB CAST: ID M_ID A_ID
# TAB GENRE ID GENRE
# TAB GENRE OF MOVIE ID M_ID G_ID
# TAB MOVIE STAFF: ID NAME
# TAB STAFF OF MOVIE: ID M_ID S_ID Job


def creation_db():
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='root',
                                 cursorclass=pymysql.cursors.Cursor)
    with connection:
        with connection.cursor() as my_cursor:
            sql = "CREATE DATABASE rt_project;"
            my_cursor.execute(sql)
        connection.commit()


def drop_db():
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='root',
                                 cursorclass=pymysql.cursors.Cursor)
    with connection:
        # with connection.cursor() as my_cursor:
        #     sql = "DROP TABLE rt_project.movies;"
        #     my_cursor.execute(sql)
        # connection.commit()
        # with connection.cursor() as my_cursor:
        #     sql = "DROP TABLE rt_project.actors;"
        #     my_cursor.execute(sql)
        # connection.commit()
        # with connection.cursor() as my_cursor:
        #     sql = "DROP TABLE rt_project.distributor;"
        #     my_cursor.execute(sql)
        # connection.commit()
        # with connection.cursor() as my_cursor:
        #     sql = "DROP TABLE rt_project.cast;"
        #     my_cursor.execute(sql)
        # connection.commit()
        # with connection.cursor() as my_cursor:
        #     sql = "DROP TABLE rt_project.genres;"
        #     my_cursor.execute(sql)
        # connection.commit()
        # with connection.cursor() as my_cursor:
        #     sql = "DROP TABLE rt_project.genre_of_movie;"
        #     my_cursor.execute(sql)
        # connection.commit()
        # with connection.cursor() as my_cursor:
        #     sql = "DROP TABLE rt_project.movie_staff;"
        #     my_cursor.execute(sql)
        # connection.commit()
        # with connection.cursor() as my_cursor:
        #     sql = "DROP TABLE rt_project.staff_of_movie;"
        #     my_cursor.execute(sql)
        # connection.commit()
        with connection.cursor() as my_cursor:
            sql = "DROP DATABASE rt_project;"
            my_cursor.execute(sql)
        connection.commit()


def connect_db():
    """Connect to db"""
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='root',
                                 database='rt_project',
                                 cursorclass=pymysql.cursors.Cursor)
    return connection


def query_db(my_query):
    """# Define query function"""
    connection = connect_db()
    with connection:
        with connection.cursor() as my_cursor:
            sql = my_query
            my_cursor.execute(sql)
            result = my_cursor.fetchall()
        connection.commit()
    return result


def query_db_many(my_query, data):
    """ QUERY MANY """
    connection = connect_db()
    with connection:
        with connection.cursor() as my_cursor:
            sql = my_query
            my_cursor.executemany(sql, data)
            result = my_cursor.fetchall()
        connection.commit()
    return result


def db_movies(nb_rows):
    """Fill the columns per table (8) per 100 lines batches:
    movies, actors, distributor, cast, staff_of_movie, movie_staff, genre_of_movie, genres
    """
    query_db("""CREATE TABLE 
    movies 
    (
      id INT, 
      title VARCHAR(255),
      tomatometer INT,
      year DATETIME,
      language VARCHAR(255),
      rating VARCHAR(255),
      distributor_id INT,
      PRIMARY KEY (id)
    )
    ;""")
    start_line = 0
    end_line = 100
    datas = data(nb_rows)
    movie_info = datas[0]
    pbar = tqdm(total=nb_rows // 100)
    cpt = 0
    while cpt <= nb_rows - 1:
        # Fill movies
        query_db_many(""" INSERT INTO rt_project.movies 
        (id, title, tomatometer, year, language, rating, distributor_id) 
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        ;""", movie_info[start_line:end_line])

        start_line += 100

        if end_line > nb_rows - 100:
            end_line = nb_rows
        else:
            end_line += 100
        pbar.update(1)
        cpt += 100

    pbar.close()


def db_actors(nb_rows):
    """ACTORS"""
    query_db("""CREATE TABLE 
    actors 
    (
      id INT, 
      full_name VARCHAR(255),
      PRIMARY KEY (id)
    )
    ;""")
    start_line = 0
    end_line = 100
    datas = data(nb_rows)
    pbar = tqdm(total=nb_rows // 100)
    cpt = 0
    cpt_id = 1
    actors = datas[2]
    while cpt <= nb_rows - 1:
        # Fill actors
        query_db_many("""INSERT INTO rt_project.actors 
              (id,full_name) 
              VALUES (%s,%s);""", actors[start_line:end_line])

        start_line += 100
        cpt_id += 1

        if end_line > nb_rows - 100:
            end_line = nb_rows
        else:
            end_line += 100
        pbar.update(1)
        cpt += 100

    pbar.close()


def db_distributors(nb_rows):
    """DISTRIBUTORS"""
    query_db("""CREATE TABLE 
    distributor 
    (
      id INT,
      name VARCHAR(255),
      PRIMARY KEY (id)
    )
    ;""")
    start_line = 0
    end_line = 100
    datas = data(nb_rows)
    pbar = tqdm(total=nb_rows // 100)
    cpt = 0
    cpt_id = 1
    distributors = datas[1]
    while cpt <= nb_rows - 1:

        # Fill distributors
        query_db_many("""INSERT INTO rt_project.distributor
                        (id,name) 
                        VALUES (%s,%s);""", distributors[start_line:end_line])

        start_line += 100
        cpt_id += 1

        if end_line > nb_rows - 100:
            end_line = nb_rows
        else:
            end_line += 100
        pbar.update(1)
        cpt += 100

    pbar.close()


def db_cast(nb_rows):
    """CAST"""
    query_db("""CREATE TABLE 
    cast 
    (
      id INT,
      movie_id INT,
      actor_id INT,
      PRIMARY KEY (id)
    )
    ;""")
    start_line = 0
    end_line = 100
    datas = data(nb_rows)
    pbar = tqdm(total=nb_rows // 100)
    cpt = 0
    cpt_id = 1
    cast = datas[3]
    while cpt <= nb_rows - 1:

        # Fill distributors
        query_db_many("""INSERT INTO rt_project.cast
        (id, movie_id, actor_id) 
        VALUES (%s,%s,%s);""", cast[start_line:end_line])

        start_line += 100
        cpt_id += 1

        if end_line > nb_rows - 100:
            end_line = nb_rows
        else:
            end_line += 100
        pbar.update(1)
        cpt += 100

    pbar.close()


def db_genre(nb_rows):
    """GENRES"""
    query_db("""CREATE TABLE 
    genres 
    (
      id INT,
      type VARCHAR(255),
      PRIMARY KEY (id)
    )
    ;""")
    start_line = 0
    end_line = 100
    datas = data(nb_rows)
    pbar = tqdm(total=nb_rows // 100)
    cpt = 0
    cpt_id = 1
    genres = datas[4]
    while cpt <= nb_rows - 1:

        # Fill distributors
        query_db_many("""INSERT INTO rt_project.genres
                        (id,type) 
                        VALUES (%s, %s);""", genres[start_line:end_line])

        start_line += 100
        cpt_id += 1

        if end_line > nb_rows - 100:
            end_line = nb_rows
        else:
            end_line += 100
        pbar.update(1)
        cpt += 100

    pbar.close()


def db_gom(nb_rows):
    """GENRE_OF_MOVIE"""
    query_db("""CREATE TABLE 
    genre_of_movie 
    (
      id INT,
      movie_id INT,
      genre_id INT,
      PRIMARY KEY (id)
    )
    ;""")
    start_line = 0
    end_line = 100
    datas = data(nb_rows)
    pbar = tqdm(total=nb_rows // 100)
    cpt = 0
    cpt_id = 1
    gom = datas[5]
    while cpt <= nb_rows - 1:

        # Fill distributors
        query_db_many("""INSERT INTO rt_project.genre_of_movie
        (id,movie_id,genre_id) 
        VALUES (%s, %s, %s);""", gom[start_line:end_line])

        start_line += 100
        cpt_id += 1

        if end_line > nb_rows - 100:
            end_line = nb_rows
        else:
            end_line += 100
        pbar.update(1)
        cpt += 100

    pbar.close()


def db_staff(nb_rows):
    """MOVIE STAFF"""
    query_db("""CREATE TABLE 
    movie_staff 
    (
      id INT,
      full_name VARCHAR(255),
      PRIMARY KEY (id)
    )
    ;""")
    start_line = 0
    end_line = 100
    datas = data(nb_rows)
    pbar = tqdm(total=nb_rows // 100)
    cpt = 0
    cpt_id = 1
    ms = datas[6]
    while cpt <= nb_rows - 1:

        # Fill distributors
        query_db_many("""INSERT INTO rt_project.movie_staff
        (id,full_name) 
        VALUES (%s, %s);""", ms[start_line:end_line])

        start_line += 100
        cpt_id += 1

        if end_line > nb_rows - 100:
            end_line = nb_rows
        else:
            end_line += 100
        pbar.update(1)
        cpt += 100

    pbar.close()


def db_staff_of_movie(nb_rows):
    """STAFF OF MOVIE"""
    query_db("""CREATE TABLE 
    staff_of_movie 
    (
      id INT,
      movie_id INT,
      staff_id INT,
      job VARCHAR(255),
      PRIMARY KEY (id)
    )
    ;""")
    start_line = 0
    end_line = 100
    datas = data(nb_rows)
    pbar = tqdm(total=nb_rows // 100)
    cpt = 0
    cpt_id = 1
    ms = datas[7]
    while cpt <= nb_rows - 1:

        # Fill distributors
        query_db_many("""INSERT INTO rt_project.staff_of_movie
        (id,movie_id,staff_id,job) 
        VALUES (%s, %s, %s, %s);""", ms[start_line:end_line])

        start_line += 100
        cpt_id += 1

        if end_line > nb_rows - 100:
            end_line = nb_rows
        else:
            end_line += 100
        pbar.update(1)
        cpt += 100

    pbar.close()


def application():
    """APPLY"""
    nb_rows = len(pd.read_csv('data_scrapped.csv'))
    try:
        creation_db()
    except pymysql.err.ProgrammingError:
        drop_db()
        creation_db()
    db_movies(nb_rows)
    db_actors(nb_rows)
    db_distributors(nb_rows)
    db_cast(nb_rows)
    db_genre(nb_rows)
    db_gom(nb_rows)
    db_staff(nb_rows)
    db_staff_of_movie(nb_rows)
    print(query_db("SELECT * FROM movies"))

