import pandas as pd

def calculate_metrics(df):

    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Pivotar os status para virar colunas
    df_pivot = df.pivot_table(
        index='timestamp',
        columns='status',
        values='count',
        aggfunc='sum',
        fill_value=0
    ).reset_index()

    # Garantir que colunas existam mesmo se algum status faltar
    for col in ['approved', 'failed', 'denied', 'reversed']:
        if col not in df_pivot.columns:
            df_pivot[col] = 0

    df_pivot['total'] = (
        df_pivot['approved'] +
        df_pivot['failed'] +
        df_pivot['denied'] +
        df_pivot['reversed']
    )

    df_pivot['failed_rate'] = df_pivot['failed'] / df_pivot['total']
    df_pivot['denied_rate'] = df_pivot['denied'] / df_pivot['total']
    df_pivot['reversed_rate'] = df_pivot['reversed'] / df_pivot['total']

    return df_pivot