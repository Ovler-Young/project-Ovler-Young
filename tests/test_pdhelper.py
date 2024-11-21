import pytest
import pandas as pd
from ia_collection_analyzer.pdhelper import normalize_list_columns

@pytest.mark.parametrize(
    "input_df,expected_df",
    [
        # Test mixed single/list values
        (
            pd.DataFrame({
                'col1': ['a', ['b', 'c'], 'd'],
                'col2': [1, [2, 3], 4]
            }),
            pd.DataFrame({
                'col1': [['a'], ['b', 'c'], ['d']],
                'col2': [[1], [2, 3], [4]]
            })
        ),
        # Test single values only (should remain unchanged)
        (
            pd.DataFrame({'col1': ['a', 'b', 'c']}),
            pd.DataFrame({'col1': ['a', 'b', 'c']})
        ),
        # Test lists only (should remain unchanged) 
        (
            pd.DataFrame({'col1': [['a'], ['b', 'c'], ['d']]}),
            pd.DataFrame({'col1': [['a'], ['b', 'c'], ['d']]})
        ),
        # Test empty DataFrame with colums
        (
            pd.DataFrame(columns=['col1']),
            pd.DataFrame(columns=['col1'])
        ),
        # Test empty DataFrame without columns
        (
            pd.DataFrame(),
            pd.DataFrame()
        ),
        # Test with None/null values
        (
            pd.DataFrame({'col1': ['a', None, ['b']]}),
            pd.DataFrame({'col1': [['a'], None, ['b']]})
        ),
        # Test multiple data types
        (
            pd.DataFrame({
                'str_col': ['a', ['b'], 'c'],
                'int_col': [1, [2], 3],
                'float_col': [1.0, [2.0], 3.0],
                'pure_list': [['x'], ['y'], ['z']]
            }),
            pd.DataFrame({
                'str_col': [['a'], ['b'], ['c']],
                'int_col': [[1], [2], [3]],
                'float_col': [[1.0], [2.0], [3.0]],
                'pure_list': [['x'], ['y'], ['z']]
            })
        )
    ]
)
def test_normalize_list_columns(input_df, expected_df):
    result = normalize_list_columns(input_df)
    pd.testing.assert_frame_equal(result, expected_df)