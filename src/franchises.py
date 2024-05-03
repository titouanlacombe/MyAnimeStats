import polars as pl

def first(col):
	return pl.col(col).first().alias(col)

def union(col):
	return pl.col(col).flatten().unique().alias(col)

def sum(col):
	return pl.col(col).sum().alias(col)

def weighted_mean(col, wh_col):
	return ((pl.col(col) * pl.col(wh_col)).sum() / pl.col(wh_col).sum()).fill_nan(None).alias(col)

# TODO change total_duration_sec to episode_avg_duration so we can calculate user_watch_duration
def get_user_franchises(user_animes: pl.DataFrame):
	# Default franchise
	user_animes = user_animes.lazy().with_columns(
		pl.col("franchise").fill_null(pl.col("title")),
	)

	# TODO aggregate user_watch_status, user_watch_start, user_watch_end, air_start, air_end
	franchises = user_animes.group_by("franchise").agg(
		sum("episodes"),
		sum("user_watch_episodes"),
		weighted_mean("scored_avg", "episodes"),
		weighted_mean("user_scored", "episodes").replace(0, None),
		union("genres"),
		union("themes"),
		union("demographics"),
		union("studios"),
		union("licensors"),
		union("producers"),
		union("source"),
		union("rating"),
		union("type"),
		pl.col("sfw").all().alias("sfw"),
		pl.col("user_rewatching").any().alias("user_rewatching"),
		sum("total_duration_sec"),
		pl.col("anime_id"),
	).sort("user_scored", descending=True, nulls_last=True)

	return franchises.collect()
