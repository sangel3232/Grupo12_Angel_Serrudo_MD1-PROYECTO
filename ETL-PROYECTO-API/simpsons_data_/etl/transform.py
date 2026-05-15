def transform_characters(df):

    print("Transformando personajes...")

    characters = df[['id', 'name', 'gender', 'occupation']]

    characters.columns = [
        'character_id',
        'name',
        'gender',
        'occupation'
    ]

    return characters


def transform_episodes(df):

    print("Transformando episodios...")

    episodes = df[['id', 'name', 'season', 'air_date']]

    episodes.columns = [
        'episode_id',
        'name',
        'season',
        'air_date'
    ]

    return episodes