# model_training.py (Polished)

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from catboost import CatBoostClassifier
from sklearn.metrics import accuracy_score
import joblib
import os

def train_model():
    """
    This script loads the customer data, performs advanced feature engineering,
    trains a CatBoost classifier, and saves the final model and necessary
    preprocessing artifacts for the Flask application.
    """
    
    # --- 1. Load Data ---
    print("--- Step 1: Loading Data ---")
    DATA_DIR = 'data'
    try:
        train_df = pd.read_csv(os.path.join(DATA_DIR, 'train.csv'))
        print("Data loaded successfully.")
    except FileNotFoundError as e:
        print(f"Error: {e}. Make sure train.csv is in the 'data/' directory.")
        return

    # --- 2. Data Preprocessing ---
    print("\n--- Step 2: Preprocessing Data ---")
    train_df = train_df.drop(['ID', 'Description'], axis=1)

    # Define feature types for clarity and robustness
    TARGET = 'Segmentation'
    NUMERICAL_FEATURES = ['Age', 'Work Experience', 'Family  Size']
    CATEGORICAL_FEATURES = ['Sex', 'Bachelor', 'Graduated', 'Career', 'Family Expenses', 'Variable']

    # Enforce numeric types and handle potential errors
    print("Enforcing numeric types for numerical features...")
    for col in NUMERICAL_FEATURES:
        train_df[col] = pd.to_numeric(train_df[col], errors='coerce')

    # Impute missing values
    print("Imputing missing values...")
    for col in NUMERICAL_FEATURES:
        if train_df[col].isnull().sum() > 0:
            train_df[col] = train_df[col].fillna(train_df[col].median())
    for col in CATEGORICAL_FEATURES:
        if train_df[col].isnull().sum() > 0:
            train_df[col] = train_df[col].fillna(train_df[col].mode()[0])

    # --- 3. Advanced Feature Engineering ---
    print("\n--- Step 3: Performing Advanced Feature Engineering ---")

    # Binning Age into meaningful groups
    train_df['Age_Group'] = pd.cut(train_df['Age'],
                                   bins=[17, 25, 35, 50, 90],
                                   labels=['18-25', '26-35', '36-50', '51+'])

    # Binning Work Experience into career levels
    train_df['Experience_Level'] = pd.cut(train_df['Work Experience'],
                                          bins=[-1, 2, 8, 20],
                                          labels=['Entry', 'Mid', 'Senior'])

    # Creating an interaction feature
    train_df['Career_Marital'] = train_df['Career'].astype(str) + '_' + train_df['Bachelor'].astype(str)

    # Update the list of categorical features with our new creations
    CATEGORICAL_FEATURES.extend(['Age_Group', 'Experience_Level', 'Career_Marital'])
    print("Feature engineering complete.")

    # --- 4. Prepare Data for Model ---
    print("\n--- Step 4: Preparing Data for the Model ---")
    y = train_df[TARGET]
    X = train_df.drop(TARGET, axis=1)

    # Enforce string type for all categorical features, as required by CatBoost
    for col in CATEGORICAL_FEATURES:
        if col in X.columns:
            X[col] = X[col].astype(str)

    # Encode the target variable (e.g., 'Akshat' -> 0)
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    # --- 5. Model Training ---
    print("\n--- Step 5: Training the Model ---")
    # Using the best parameters we found from previous tuning
    best_params = {'depth': 4, 'iterations': 500, 'l2_leaf_reg': 3, 'learning_rate': 0.05}

    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)

    model = CatBoostClassifier(
        **best_params,
        loss_function='MultiClass',
        eval_metric='Accuracy',
        cat_features=CATEGORICAL_FEATURES,
        random_seed=42,
        verbose=100
    )

    # Use early stopping to prevent overfitting and find the best iteration
    model.fit(X_train, y_train, eval_set=(X_test, y_test), early_stopping_rounds=50)

    # --- 6. Model Evaluation ---
    print("\n--- Step 6: Evaluating the Final Model ---")
    final_preds = model.predict(X_test)
    final_accuracy = accuracy_score(y_test, final_preds)
    print(f"Final Model Validation Accuracy: {final_accuracy:.4f}")

    # --- 7. Save Model and Artifacts ---
    print("\n--- Step 7: Saving Model and Artifacts ---")
    output_dir = 'model'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    joblib.dump(model, os.path.join(output_dir, 'catboost_model.pkl'))
    joblib.dump(le, os.path.join(output_dir, 'label_encoder.pkl'))
    model_columns = X.columns.tolist()
    joblib.dump(model_columns, os.path.join(output_dir, 'model_columns.pkl'))

    print("\nModel and artifacts saved successfully in the 'model/' directory.")
    print("Training script finished.")

if __name__ == '__main__':
    train_model()
