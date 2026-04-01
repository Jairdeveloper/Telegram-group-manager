import json
import numpy as np
import logging
from sklearn.model_selection import train_test_split

from app.nlp.features import FeatureExtractor
from app.nlp.classifiers.ml_classifier import MLIntentClassifier
from app.nlp.calibration import ConfidenceCalibrator
from app.nlp.tokenizer import NLPTokenizer
from app.nlp.serialization import ModelSerializationManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_training_data(data_path: str = "data/intent_training_data.json"):
    """Cargar datos de entrenamiento desde JSON"""
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['training_data'], data['metadata']


def prepare_features_and_labels(training_data, tokenizer):
    """Preparar features y labels para entrenamiento"""
    texts = [item['text'] for item in training_data]
    labels = [item['intent'] for item in training_data]

    logger.info(f"Tokenizing {len(texts)} texts...")
    tokenization_results = []
    for i, text in enumerate(texts):
        result = tokenizer.tokenize(text)
        tokenization_results.append(result)
        if (i + 1) % 100 == 0:
            logger.info(f"  Tokenized {i + 1}/{len(texts)}")

    return tokenization_results, labels


def main():
    """Main training and serialization pipeline"""
    logger.info("=" * 60)
    logger.info("TRAINING AND SERIALIZATION PIPELINE")
    logger.info("=" * 60)

    logger.info("\n[1/6] Loading training data...")
    training_data, metadata = load_training_data()
    logger.info(f"  Loaded {len(training_data)} examples")

    logger.info("\n[2/6] Tokenizing training data...")
    tokenizer = NLPTokenizer()
    tokenization_results, labels = prepare_features_and_labels(training_data, tokenizer)
    logger.info(f"  Tokenization complete")

    logger.info("\n[3/6] Extracting features...")
    feature_extractor = FeatureExtractor(max_features=50)
    texts_for_fitting = [tr.text for tr in tokenization_results]
    feature_extractor.fit(texts_for_fitting)

    X = np.array([feature_extractor.extract(tr) for tr in tokenization_results])
    y = np.array(labels)
    logger.info(f"  Feature matrix shape: {X.shape}")

    logger.info("\n[4/6] Splitting data (80/20 stratified)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    logger.info(f"  Train set: {X_train.shape[0]} samples")
    logger.info(f"  Test set: {X_test.shape[0]} samples")

    logger.info("\n[5/6] Training model...")
    classifier = MLIntentClassifier(model_path="models/intent_classifier.joblib")
    classifier.set_feature_extractor(feature_extractor)
    
    training_result = classifier.train(X_train, y_train.tolist(), hyperparameter_tuning=True)
    logger.info(f"  Best params: {training_result.get('best_params', 'N/A')}")
    logger.info(f"  Best CV score: {training_result.get('best_cv_score', 'N/A'):.4f}")

    logger.info("\n[5.5/6] Training confidence calibrator...")
    calibrator = ConfidenceCalibrator()
    calibrator.class_labels = list(classifier.classes)
    calibrator.fit(
        classifier.model.predict_proba(X_test),
        np.array([list(classifier.classes).index(label) for label in y_test])
    )
    logger.info("  Calibrator trained")

    logger.info("\n[6/6] Evaluating model...")
    eval_result = classifier.evaluate(X_test, y_test.tolist())
    
    logger.info("\n" + "=" * 60)
    logger.info("EVALUATION RESULTS")
    logger.info("=" * 60)
    logger.info(f"Accuracy:  {eval_result['accuracy']:.4f}")
    logger.info(f"Precision: {eval_result['precision']:.4f}")
    logger.info(f"Recall:    {eval_result['recall']:.4f}")
    logger.info(f"F1:        {eval_result['f1']:.4f}")

    logger.info("\n[7/7] Serializing all models...")
    serialization_manager = ModelSerializationManager(models_dir="models")
    
    serialization_results = serialization_manager.save_all_models(
        intent_classifier=classifier.model,
        feature_extractor=feature_extractor,
        confidence_calibrator=calibrator,
        metadata={
            'training_result': {
                'best_params': training_result.get('best_params'),
                'best_cv_score': training_result.get('best_cv_score')
            },
            'evaluation_result': {
                'accuracy': eval_result['accuracy'],
                'precision': eval_result['precision'],
                'recall': eval_result['recall'],
                'f1': eval_result['f1']
            }
        }
    )
    
    verification = serialization_manager.verify_models()
    logger.info(f"\nVerification: {verification['status']}")

    info = serialization_manager.get_model_info()
    logger.info("\nModel files created:")
    for model_name, model_info in info.get('models', {}).items():
        logger.info(f"  - {model_name}: {model_info['size_mb']} MB")

    logger.info("\n" + "=" * 60)
    logger.info("TRAINING AND SERIALIZATION COMPLETED")
    logger.info("=" * 60)

    return {
        'evaluation': eval_result,
        'training_result': training_result,
        'serialization': serialization_results,
        'verification': verification
    }


if __name__ == "__main__":
    results = main()