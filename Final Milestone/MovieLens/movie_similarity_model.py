import heapq
from collections import defaultdict
from collections import namedtuple

import numpy as np

from baseline_models import BaselineEffectsModel
from baseline_models import BaselineModel
from common import elapsed_time
from common import score_model
from read_ratings import read_ratings_df_with_timestamp

MovieSimilarity = namedtuple('MovieSimilarity', ['movie_id', 'similarity'])


class MovieSimilarityModel(BaselineModel):
    def __init__(self, k_neighbors=40):
        self.k_neighbors = k_neighbors

        self.baseline_model = BaselineEffectsModel()
        self.ratings_by_movie = defaultdict(dict)
        self.ratings_by_user = defaultdict(dict)
        self.raters_by_movie = {}
        self.movie_similarity = {}
        # self.movie_aij = {}

    def set_k_neighbors(self, k_neighbors):
        self.k_neighbors = k_neighbors

    def calculate_common_raters(self, movie_id_1, movie_id_2):
        raters1 = self.raters_by_movie[movie_id_1]
        raters2 = self.raters_by_movie[movie_id_2]
        return raters1 & raters2

    def get_common_ratings(self, movie_id, raters):
        all_ratings = self.ratings_by_movie[movie_id]
        ratings = []
        for rater_id in raters:
            ratings.append(all_ratings[rater_id])

        return np.array(ratings)

    def calculate_similarity(self, movie_id_1, movie_id_2):
        common_raters = self.calculate_common_raters(movie_id_1, movie_id_2)
        support = len(common_raters)
        if support <= 1:
            similarity = 0.0
            # aij = 0.0
        else:
            ratings1 = self.get_common_ratings(movie_id_1, common_raters)
            ratings2 = self.get_common_ratings(movie_id_2, common_raters)

            alpha = 4.0

            similarity = support / (np.power(ratings1 - ratings2, 2).sum() + alpha)

            # aij = np.multiply(ratings1, ratings2).sum() / support

        return similarity

    def fit(self, ratings_df):
        with elapsed_time('fit'):
            self.baseline_model.fit(ratings_df)

            ratings_df = self.baseline_model.create_modified_ratings(ratings_df)

            unique_movie_ids = np.array(sorted(ratings_df['movieId'].unique()))

            for _, row in ratings_df.iterrows():
                movie_id = row['movieId']
                user_id = row['userId']
                rating = row['rating']
                self.ratings_by_movie[movie_id][user_id] = rating
                self.ratings_by_user[user_id][movie_id] = rating

            for movie_id in unique_movie_ids:
                self.raters_by_movie[movie_id] = set(self.ratings_by_movie[movie_id].keys())

            for movie_index_1, movie_id_1 in enumerate(unique_movie_ids):
                for movie_index_2 in xrange(movie_index_1 + 1, len(unique_movie_ids)):
                    movie_id_2 = unique_movie_ids[movie_index_2]

                    similarity = self.calculate_similarity(movie_id_1, movie_id_2)
                    movie_pair = (movie_id_1, movie_id_2)
                    self.movie_similarity[movie_pair] = similarity
                    # self.movie_aij[movie_pair] = aij

        return self

    def get_similarity(self, movie_id_1, movie_id_2):
        if movie_id_1 < movie_id_2:
            id_1 = movie_id_1
            id_2 = movie_id_2
        else:
            id_1 = movie_id_2
            id_2 = movie_id_1

        return self.movie_similarity.get((id_1, id_2), -1.0)

    def clear_predict_caches(self):
        self.zero_prediction_count = 0

    def predict_rating(self, user_id, movie_id):
        ratings = self.ratings_by_user[user_id]

        elements = []

        for movie_id_2 in ratings:
            if movie_id != movie_id_2:
                similarity = self.get_similarity(movie_id, movie_id_2)
                if similarity > 0.0:
                    elements.append(MovieSimilarity(movie_id_2, similarity))

        movie_similarities = heapq.nlargest(self.k_neighbors, elements, key=lambda e: e.similarity)

        if len(movie_similarities) > 0:
            similarity_sum = 0.0
            product_sum = 0.0
            for movie_similarity in movie_similarities:
                movie_id_2 = movie_similarity.movie_id
                rating = ratings[movie_id_2]
                similarity = movie_similarity.similarity

                product_sum += similarity * rating
                similarity_sum += similarity

            rating = product_sum / similarity_sum
        else:
            rating = 0.0
            self.zero_prediction_count += 1

        result = self.baseline_model.predict_baseline_rating(user_id, movie_id) + rating

        return result

    def predict(self, x):
        self.clear_predict_caches()
        predictions = [self.predict_rating(row['userId'], row['movieId']) for _, row in x.iterrows()]
        print 'used baseline predictions: %.1f%%' % (100.0 * self.zero_prediction_count / len(predictions))
        return predictions


def main():
    ratings_df = read_ratings_df_with_timestamp('ml-latest-small/ratings.csv')
    # ratings_df = read_ratings_df('ml-latest-small/ratings_5_pct.csv')

    with elapsed_time('score model'):
        score_model(ratings_df, model_f=MovieSimilarityModel, model_name='movie similarity model')


if __name__ == '__main__':
    main()
