#!/usr/bin/env python3
"""
アンサンブルモデルデバッグ用スクリプト
"""

import joblib
import pandas as pd
import numpy as np

def debug_ensemble():
    """アンサンブルモデルをデバッグ"""
    try:
        # アンサンブルモデルと前処理器を読み込み
        model = joblib.load('src/ml/models/trained/house_price_ensemble_duckdb.pkl')
        preprocessor = joblib.load('src/ml/models/trained/house_price_ensemble_duckdb_preprocessor.pkl')
        print('✅ アンサンブルモデル読み込み成功')
        
        # モデル情報を確認
        print(f'🔍 モデルタイプ: {type(model)}')
        print(f'🔍 モデル属性: {dir(model)}')
        
        # 前処理器情報を確認
        print(f'🔍 前処理器タイプ: {type(preprocessor)}')
        print(f'🔍 前処理器属性: {dir(preprocessor)}')
        
        # サンプルデータを作成（複数のパターンを試す）
        sample_data_1 = pd.DataFrame({
            'sqft': [2000], 
            'bedrooms': [3], 
            'bathrooms': [2.5], 
            'year_built': [2000], 
            'location': ['Suburb'], 
            'condition': ['Good']
        })
        
        sample_data_2 = pd.DataFrame({
            'sqft': [2000], 
            'bedrooms': [3], 
            'bathrooms': [2.5], 
            'house_age': [25], 
            'price_per_sqft': [200], 
            'bed_bath_ratio': [1.2], 
            'location': ['Suburb'], 
            'condition': ['Good']
        })
        
        print(f'📊 サンプルデータ1:')
        print(sample_data_1)
        print(f'📊 サンプルデータ2:')
        print(sample_data_2)
        
        # パターン1を試す
        try:
            current_year = 2025
            sample_data_1['house_age'] = current_year - sample_data_1['year_built']
            sample_data_1['price_per_sqft'] = 200
            sample_data_1['bed_bath_ratio'] = sample_data_1['bedrooms'] / sample_data_1['bathrooms']
            
            X_transformed_1 = preprocessor.transform(sample_data_1)
            print(f'🔧 パターン1前処理後データ形状: {X_transformed_1.shape}')
            
            prediction_1 = model.predict(X_transformed_1)
            print(f'📈 パターン1予測結果: ${prediction_1[0]:,.2f}')
        except Exception as e:
            print(f'❌ パターン1エラー: {e}')
        
        # パターン2を試す
        try:
            X_transformed_2 = preprocessor.transform(sample_data_2)
            print(f'🔧 パターン2前処理後データ形状: {X_transformed_2.shape}')
            
            prediction_2 = model.predict(X_transformed_2)
            print(f'📈 パターン2予測結果: ${prediction_2[0]:,.2f}')
        except Exception as e:
            print(f'❌ パターン2エラー: {e}')
        
        return True
        
    except Exception as e:
        print(f'❌ エラー: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_ensemble() 