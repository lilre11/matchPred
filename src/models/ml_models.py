import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import xgboost as xgb
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
import joblib
import logging
from typing import Dict, Tuple, Any
import os

class MLModelTrainer:
    """
    Machine Learning model trainer for Spor Toto predictions
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.models = {}
        self.logger = logging.getLogger(__name__)
        
    def train_models(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """
        Train multiple ML models for ensemble prediction
        """
        self.logger.info("Starting model training process")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=self.config['test_size'],
            random_state=self.config['random_state'],
            stratify=y
        )
        
        results = {}
        
        # Train Random Forest
        self.logger.info("Training Random Forest model")
        rf_model, rf_score = self._train_random_forest(X_train, X_test, y_train, y_test)
        self.models['random_forest'] = rf_model
        results['random_forest'] = rf_score
        
        # Train XGBoost
        self.logger.info("Training XGBoost model")
        xgb_model, xgb_score = self._train_xgboost(X_train, X_test, y_train, y_test)
        self.models['xgboost'] = xgb_model
        results['xgboost'] = xgb_score
        
        # Train Neural Network
        self.logger.info("Training Neural Network model")
        nn_model, nn_score = self._train_neural_network(X_train, X_test, y_train, y_test)
        self.models['neural_network'] = nn_model
        results['neural_network'] = nn_score
        
        # Save models
        self._save_models()
        
        self.logger.info(f"Model training completed. Results: {results}")
        return results
    
    def _train_random_forest(self, X_train: pd.DataFrame, X_test: pd.DataFrame, 
                           y_train: pd.Series, y_test: pd.Series) -> Tuple[Any, Dict]:
        """Train Random Forest model"""
        
        rf_config = self.config['models']['random_forest']
        
        model = RandomForestClassifier(
            n_estimators=rf_config['n_estimators'],
            max_depth=rf_config['max_depth'],
            min_samples_split=rf_config['min_samples_split'],
            random_state=self.config['random_state'],
            n_jobs=-1
        )
        
        # Train model
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(
            model, X_train, y_train, 
            cv=self.config['cross_validation_folds'],
            scoring='accuracy'
        )
        
        results = {
            'test_accuracy': accuracy,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'feature_importance': dict(zip(X_train.columns, model.feature_importances_))
        }
        
        return model, results
    
    def _train_xgboost(self, X_train: pd.DataFrame, X_test: pd.DataFrame,
                      y_train: pd.Series, y_test: pd.Series) -> Tuple[Any, Dict]:
        """Train XGBoost model"""
        
        xgb_config = self.config['models']['xgboost']
        
        model = xgb.XGBClassifier(
            n_estimators=xgb_config['n_estimators'],
            learning_rate=xgb_config['learning_rate'],
            max_depth=xgb_config['max_depth'],
            random_state=self.config['random_state'],
            eval_metric='mlogloss'
        )
        
        # Train model
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(
            model, X_train, y_train,
            cv=self.config['cross_validation_folds'],
            scoring='accuracy'
        )
        
        results = {
            'test_accuracy': accuracy,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'feature_importance': dict(zip(X_train.columns, model.feature_importances_))
        }
        
        return model, results
    
    def _train_neural_network(self, X_train: pd.DataFrame, X_test: pd.DataFrame,
                            y_train: pd.Series, y_test: pd.Series) -> Tuple[Any, Dict]:
        """Train Neural Network model"""
        
        nn_config = self.config['models']['neural_network']
        
        # Build model
        model = Sequential()
        
        # Input layer
        model.add(Dense(nn_config['hidden_layers'][0], 
                       activation='relu', 
                       input_shape=(X_train.shape[1],)))
        model.add(Dropout(0.3))
        
        # Hidden layers
        for units in nn_config['hidden_layers'][1:]:
            model.add(Dense(units, activation='relu'))
            model.add(Dropout(0.3))
        
        # Output layer (3 classes: Win, Draw, Loss)
        model.add(Dense(3, activation='softmax'))
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Train model
        history = model.fit(
            X_train, y_train,
            epochs=nn_config['epochs'],
            batch_size=nn_config['batch_size'],
            validation_split=0.2,
            verbose=0
        )
        
        # Evaluate
        y_pred_proba = model.predict(X_test)
        y_pred = np.argmax(y_pred_proba, axis=1)
        accuracy = accuracy_score(y_test, y_pred)
        
        results = {
            'test_accuracy': accuracy,
            'train_accuracy': history.history['accuracy'][-1],
            'val_accuracy': history.history['val_accuracy'][-1],
            'train_loss': history.history['loss'][-1],
            'val_loss': history.history['val_loss'][-1]
        }
        
        return model, results
    
    def _save_models(self):
        """Save trained models"""
        
        models_dir = self.config.get('models_dir', 'data/models')
        os.makedirs(models_dir, exist_ok=True)
        
        # Save sklearn models
        for name, model in self.models.items():
            if name in ['random_forest', 'xgboost']:
                joblib.dump(model, f"{models_dir}/{name}_model.pkl")
        
        # Save neural network separately
        if 'neural_network' in self.models:
            self.models['neural_network'].save(f"{models_dir}/neural_network_model.h5")
        
        self.logger.info(f"Models saved to {models_dir}")
    
    def load_models(self, models_dir: str = None):
        """Load pre-trained models"""
        
        if models_dir is None:
            models_dir = self.config.get('models_dir', 'data/models')
        
        # Load sklearn models
        for model_name in ['random_forest', 'xgboost']:
            model_path = f"{models_dir}/{model_name}_model.pkl"
            if os.path.exists(model_path):
                self.models[model_name] = joblib.load(model_path)
                self.logger.info(f"Loaded {model_name} model")
        
        # Load neural network
        nn_path = f"{models_dir}/neural_network_model.h5"
        if os.path.exists(nn_path):
            from tensorflow.keras.models import load_model
            self.models['neural_network'] = load_model(nn_path)
            self.logger.info("Loaded neural network model")
    
    def get_feature_importance(self) -> Dict:
        """Get feature importance from tree-based models"""
        
        importance_dict = {}
        
        for model_name in ['random_forest', 'xgboost']:
            if model_name in self.models:
                model = self.models[model_name]
                if hasattr(model, 'feature_importances_'):
                    importance_dict[model_name] = model.feature_importances_
        
        return importance_dict
