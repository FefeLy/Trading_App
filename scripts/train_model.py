from app.data.loaders import load_binance_klines
from app.data.cleaners import clean_market_data
from app.features.technicals import add_technicals
from app.models.registry import prepare_dataset
from app.models.ml_models import LogisticSignalModel


def main():
    print("📥 Loading market data...")
    df = load_binance_klines("BTCUSDT", "1h", 1500)
    df = clean_market_data(df)
    df = add_technicals(df)

    print("🧠 Preparing dataset...")
    X, y = prepare_dataset(df)

    print("🤖 Training model...")
    model = LogisticSignalModel()
    model.train(X, y)

    print("✅ Model trained successfully")


if __name__ == "__main__":
    main()
