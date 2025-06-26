#!/usr/bin/env python3
"""
モデルテスト用スクリプト
"""

import joblib
import pandas as pd
import numpy as np

def test_model():
    """モデルをテスト"""
    try:
        # モデルと前処理器を読み込み
        model = joblib.load('src/ml/models/trained/house_price_prediction.pkl')
        preprocessor = joblib.load('src/ml/models/trained/house_price_prediction_encoders.pkl')
        print('✅ モデル読み込み成功')
        
        # サンプルデータを作成
        sample_data = pd.DataFrame({
            'sqft': [2000], 
            'bedrooms': [3], 
            'bathrooms': [2.5], 
            'year_built': [2000], 
            'location': ['Suburb'], 
            'condition': ['Good']
        })
        
        # 特徴量エンジニアリング
        current_year = 2025
        sample_data['house_age'] = current_year - sample_data['year_built']
        sample_data['price_per_sqft'] = 200
        sample_data['bed_bath_ratio'] = sample_data['bedrooms'] / sample_data['bathrooms']
        
        print(f'📊 入力データ:')
        print(sample_data)
        
        # 前処理
        X_transformed = preprocessor.transform(sample_data)
        print(f'🔧 前処理後データ形状: {X_transformed.shape}')
        
        # 予測
        prediction = model.predict(X_transformed)
        print(f'📈 サンプル予測結果: ${prediction[0]:,.2f}')
        
        return True
        
    except Exception as e:
        print(f'❌ エラー: {e}')
        return False

if __name__ == "__main__":
    test_model() 