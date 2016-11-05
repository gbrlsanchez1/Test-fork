import operator
from collections import defaultdict
from collections import namedtuple, Counter
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import display

Dataset = namedtuple('Dataset', ['ratings_df', 'movies_df', 'tags_df', 'links_df'])


def date_parse(time_in_secs):
    return datetime.utcfromtimestamp(float(time_in_secs))


def read_data():
    ratings_df = pd.read_csv('ml-latest-small/ratings.csv', parse_dates=['timestamp'], date_parser=date_parse)
    movies_df = pd.read_csv('ml-latest-small/movies.csv')
    tags_df = pd.read_csv('ml-latest-small/tags.csv', parse_dates=['timestamp'], date_parser=date_parse)
    links_df = pd.read_csv('ml-latest-small/links.csv')
    return Dataset(ratings_df, movies_df, tags_df, links_df)


def explore_data(dataset):
    ratings_df = dataset.ratings_df
    movies_df = dataset.movies_df
    tags_df = dataset.tags_df
    links_df = dataset.links_df

    merged_movies_df = movies_df.merge(links_df)
    merged_ratings_df = ratings_df.merge(merged_movies_df)
    merged_tags_df = tags_df.merge(merged_movies_df)

    print 'raw ratings data:'
    display(ratings_df.head())
    print

    print 'raw movies data:'
    display(movies_df.head())
    print

    print 'raw tags data:'
    display(tags_df.head())
    print

    print 'raw links data:'
    display(links_df.head())
    print

    print 'merged movies data:'
    display(merged_movies_df.head())
    print

    print 'merged ratings data:'
    display(merged_ratings_df.head())
    print

    print 'merged tags data:'
    display(merged_tags_df.head())
    print


def get_fig_size(nrows=1):
    return 15, 10 * nrows


def show_ratings_histogram(ratings):
    _, ax = plt.subplots(1, 1, figsize=get_fig_size())

    ax.hist(ratings, bins=np.arange(0.25, 5.5, step=0.5), alpha=0.4)

    ratings_mean = ratings.mean()

    ax.axvline(x=ratings_mean, linewidth=3, color='k')
    plt.text(ratings_mean - 0.55, 25000, 'mean = %.2f' % ratings_mean)

    ax.set_xlabel('rating')
    ax.set_ylabel('count')
    ax.set_title('Overall ratings')

    plt.tight_layout()
    plt.show()


def explore_basic_stats(dataset):
    ratings_df = dataset.ratings_df
    movies_df = dataset.movies_df

    user_ids = ratings_df['userId']
    ratings = ratings_df['rating']

    print 'How many ratings? {:,}'.format(len(ratings_df))

    user_id_counter = Counter(user_ids)

    print 'How many users?', len(user_id_counter)
    print 'How many movies? {:,}'.format(len(movies_df))

    ratings_counter = Counter(ratings)

    print 'How many unique ratings?', len(ratings_counter.keys())
    print 'Unique rating values:', sorted(ratings_counter.keys())
    print 'Overall ratings mean: {:.2f}'.format(ratings.mean())

    show_ratings_histogram(ratings)


def explore_num_ratings_per_user(dataset):
    ratings_df = dataset.ratings_df
    user_ids = ratings_df['userId']

    user_id_counter = Counter(user_ids)
    num_ratings_per_user = user_id_counter.values()

    mean = np.mean(num_ratings_per_user)
    print 'The maximum number of ratings per user: %.0f' % np.max(num_ratings_per_user)
    print 'The mean number of ratings per user: %.2f' % mean
    print 'The minimum number of ratings per user: %.0f' % np.min(num_ratings_per_user)

    _, ax = plt.subplots(1, 1, figsize=get_fig_size())

    ax.hist(num_ratings_per_user, bins=np.logspace(1, 4, num=50), alpha=0.4)

    ax.axvline(x=mean, linewidth=2, color='k')
    plt.text(mean + 30, 37, 'mean = %.2f' % mean)

    ax.set_xscale('log')
    ax.set_xlabel('number of ratings per user (log scale)')
    ax.set_ylabel('count')
    ax.set_title('Number of ratings per user (log scale)')

    plt.tight_layout()
    plt.show()


def explore_user_mean_ratings(dataset):
    ratings_df = dataset.ratings_df

    user_ratings = ratings_df.groupby('userId')['rating'].mean()

    print 'The maximum user mean rating: %.2f' % user_ratings.max()
    user_ratings_mean = user_ratings.mean()
    print 'The mean user mean rating: %.2f' % user_ratings_mean
    print 'The minimum user mean rating: %.2f' % user_ratings.min()

    _, ax = plt.subplots(1, 1, figsize=get_fig_size())

    ax.hist(user_ratings, bins=50, alpha=0.4)

    ax.axvline(x=user_ratings_mean, linewidth=3, color='k')
    plt.text(user_ratings_mean + 0.05, 57, 'mean = %.2f' % user_ratings_mean)

    ax.set_xlabel('user mean rating')
    ax.set_ylabel('count')
    ax.set_title('User mean ratings')

    plt.tight_layout()
    plt.show()


def explore_num_ratings_per_movie(dataset):
    ratings_df = dataset.ratings_df
    movie_ids = ratings_df['movieId']

    movie_id_counter = Counter(movie_ids)
    num_ratings_per_movie = movie_id_counter.values()

    mean = np.mean(num_ratings_per_movie)
    print 'The maximum number of ratings per movie: %.0f' % np.max(num_ratings_per_movie)
    print 'The mean number of ratings per movie: %.2f' % mean
    print 'The minimum number of ratings per movie: %.0f' % np.min(num_ratings_per_movie)

    num_ratings_per_movie_counter = Counter(num_ratings_per_movie)

    print 'Number of movies with one rating: {:,}'.format(num_ratings_per_movie_counter[1])
    print 'Number of movies with two ratings: {:,}'.format(num_ratings_per_movie_counter[2])

    _, ax = plt.subplots(1, 1, figsize=get_fig_size())

    ax.hist(num_ratings_per_movie, bins=np.logspace(0.0, 3.0, num=15), alpha=0.4)

    ax.axvline(x=mean, linewidth=2, color='k')
    plt.text(mean + 1, 3200, 'mean = %.2f' % mean)

    ax.set_xscale('log')
    ax.set_xlabel('number of ratings per movie (log scale)')
    ax.set_ylabel('count')
    ax.set_title('Number of ratings per movie (log scale)')

    plt.tight_layout()
    plt.show()


def explore_movie_mean_ratings(dataset):
    ratings_df = dataset.ratings_df

    movie_ratings = ratings_df.groupby('movieId')['rating']

    movie_mean_ratings = movie_ratings.mean()

    print 'The maximum movie mean rating: %.2f' % movie_mean_ratings.max()
    movie_ratings_mean = movie_mean_ratings.mean()
    print 'The mean movie mean rating: %.2f' % movie_ratings_mean
    print 'The minimum movie mean rating: %.2f' % movie_mean_ratings.min()

    _, ax = plt.subplots(1, 1, figsize=get_fig_size())

    ax.hist(movie_mean_ratings, bins=50, alpha=0.4)

    ax.axvline(x=movie_ratings_mean, linewidth=3, color='k')
    plt.text(movie_ratings_mean + 0.05, 1150, 'mean = %.2f' % movie_ratings_mean)

    ax.set_xlabel('movie mean rating')
    ax.set_ylabel('count')
    ax.set_title('Movie mean ratings')

    plt.tight_layout()
    plt.show()


def explore_user_num_ratings_vs_mean_rating(dataset):
    ratings_df = dataset.ratings_df
    user_ratings = ratings_df.groupby('userId')['rating']

    user_agg = user_ratings.agg({'mean_rating': np.mean, 'count': 'count'})

    _, ax = plt.subplots(1, 1, figsize=get_fig_size())

    ax.scatter(user_agg['mean_rating'], user_agg['count'])

    ax.set_yscale('log')
    ax.set_xlabel('user mean rating')
    ax.set_ylabel('number of ratings per user (log scale)')
    ax.set_title('number of ratings per user (log scale) vs user mean rating')

    plt.tight_layout()
    plt.show()


def explore_movie_num_ratings_vs_mean_rating(dataset):
    ratings_df = dataset.ratings_df
    movie_ratings = ratings_df.groupby('movieId')['rating']

    movie_agg = movie_ratings.agg({'mean_rating': np.mean, 'count': 'count'})

    _, ax = plt.subplots(1, 1, figsize=get_fig_size())

    ax.scatter(movie_agg['mean_rating'], movie_agg['count'])

    ax.set_yscale('log')
    ax.set_xlabel('movie mean rating')
    ax.set_ylabel('number of ratings per movie (log scale)')
    ax.set_title('number of ratings per movie (log scale) vs movie mean rating')

    plt.tight_layout()
    plt.show()


def explore_review_dates(dataset):
    ratings_df = dataset.ratings_df
    dates = ratings_df['timestamp']

    mpl_dates = mdates.date2num(dates.astype(datetime))

    print 'The range of review dates, min: %s, max: %s' % (np.min(dates), np.max(dates))

    _, ax = plt.subplots(1, 1, figsize=get_fig_size())

    ax.hist(mpl_dates, bins=50, alpha=0.4)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

    ax.set_xlabel('review date')
    ax.set_ylabel('count')
    ax.set_title('Review dates distribution')

    plt.tight_layout()
    plt.show()


def get_genre_list(genre):
    if genre == '(no genres listed)':
        return []
    return genre.split('|')


def explore_num_genres_per_movie(dataset):
    movies_df = dataset.movies_df
    genres = movies_df['genres']

    genre_list = []
    num_genres_per_movie = []
    for genre in genres:
        movie_genres = get_genre_list(genre)
        genre_list.extend(movie_genres)
        num_genres_per_movie.append(len(movie_genres))

    genre_set = set(genre_list)
    print 'Number of genres: ', len(genre_set)
    print 'Genres: ', sorted(genre_set)

    print 'Maximum genres per movie: ', np.max(num_genres_per_movie)
    mean = np.mean(num_genres_per_movie)
    print 'Mean genres per movie: %.2f' % mean
    print 'Minimum genres per movie: ', np.min(num_genres_per_movie)

    counter = Counter(num_genres_per_movie)

    print 'Number of movies with zero genres: ', counter[0]

    _, ax = plt.subplots(1, 1, figsize=get_fig_size())

    ax.hist(num_genres_per_movie, bins=np.arange(-0.5, 11.0, step=1.0), alpha=0.4)

    ax.axvline(x=mean, linewidth=2, color='k')
    plt.text(mean + 0.1, 3300, 'mean = %.2f' % mean)

    ax.set_xlabel('number of genres per movie')
    ax.set_ylabel('count')
    ax.set_title('Number of genres per movie')

    plt.tight_layout()
    plt.show()


def explore_num_movies_per_genre(dataset):
    movies_df = dataset.movies_df
    genres = movies_df['genres']

    genre_dict = defaultdict(int)
    for movie_index, genre in enumerate(genres):
        genres = get_genre_list(genre)
        for g in genres:
            genre_dict[g] += 1

    sorted_genres = sorted(genre_dict.items(), key=operator.itemgetter(1), reverse=True)

    print 'Sorted number of movies per genre: \n', sorted_genres

    _, ax = plt.subplots(1, 1, figsize=get_fig_size())

    # ax.hist(num_genres_per_movie, bins=np.arange(-0.5, 11.0, step=1.0), alpha=0.4)

    # ax.bar([g[1] for g in sorted_genres], [g[0] for g in sorted_genres])

    # ax.set_xlabel('number of genres per movie')
    # ax.set_ylabel('count')
    # ax.set_title('Number of genres per movie')

    plt.tight_layout()
    plt.show()


def main():
    dataset = read_data()

    # explore_data(dataset)
    # explore_basic_stats(dataset)

    # explore_num_ratings_per_user(dataset)
    # explore_user_mean_ratings(dataset)
    # explore_num_ratings_per_movie(dataset)
    # explore_movie_mean_ratings(dataset)
    # explore_user_num_ratings_vs_mean_rating(dataset)
    # explore_movie_num_ratings_vs_mean_rating(dataset)
    # explore_review_dates(dataset)

    # explore_num_genres_per_movie(dataset)
    explore_num_movies_per_genre(dataset)


if __name__ == '__main__':
    main()
