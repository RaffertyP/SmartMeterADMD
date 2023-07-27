import pandas as pd
import statsmodels.api as sm

def build_linear_models(df):
    result_data = []
    df_regression = pd.DataFrame(columns=['DwellingType', 'ICP_Property_Floor_Area', 'kW2022_WinterPeakMetered'])

    for category_value in df['DwellingType'].unique():
        df_subset = df[df['DwellingType'] == category_value]
        X = df_subset['ICP_Property_Floor_Area']
        y = df_subset['kW2022_WinterPeakMetered']

        X = sm.add_constant(X)
        model = sm.OLS(y, X).fit()

        m = model.params['ICP_Property_Floor_Area']
        c = model.params['const']
        r_squared = model.rsquared

        result_data.append({'DwellingType': category_value, 'm': m, 'c': c, 'R_squared': r_squared})

        # Build the regression DataFrame for FloorArea between 60 and 500
        floor_area_values = range(60, 501)
        df_temp = pd.DataFrame({'DwellingType': [category_value] * len(floor_area_values),
                                'ICP_Property_Floor_Area': floor_area_values})
        df_regression = pd.concat([df_regression, df_temp], ignore_index=True)

    result_df = pd.DataFrame(result_data)

    # Merge the regression DataFrame with the result DataFrame
    df_regression = df_regression.merge(result_df, on=['DwellingType'])

    # Calculate kW2022_WinterPeakMetered using the linear model coefficients
    df_regression['kW2022_WinterPeakMetered'] = df_regression['ICP_Property_Floor_Area'] * df_regression['m'] + df_regression['c']

    return result_df, df_regression
