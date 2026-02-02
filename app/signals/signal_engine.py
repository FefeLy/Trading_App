import pandas as pd

from app.models.registry import get_active_model
from app.risk.stop_loss import compute_stop_loss
from app.risk.take_profit import compute_take_profit
from app.core.signal_types import SignalType

# AI (opcional pero seguro)
try:
    from app.ai.market_regime import detect_regime, MarketRegime
except ImportError:
    detect_regime = None
    MarketRegime = None


class SignalEngine:
    """
    Motor institucional de señales (PRO):
    - ML para probabilidad (BUY bias)
    - Confirmación técnica institucional (EMA/RSI/MACD/ADX/VWAP/VOL)
    - Régimen manda (bull/bear/range/dead)
    """

    def __init__(self, threshold: float = 0.55):
        self.model = get_active_model()
        self.threshold = float(threshold)

        if not hasattr(self.model, "predict_proba"):
            raise RuntimeError("Active model has no predict_proba method")

        if not hasattr(self.model, "feature_columns"):
            raise RuntimeError("Active model has no feature_columns attribute")

        # blindaje
        if self.threshold < 0.50:
            self.threshold = 0.50
        if self.threshold > 0.90:
            self.threshold = 0.90

    # ============================
    # ✅ Helpers
    # ============================
    def _getf(self, df: pd.DataFrame, col: str, default=None):
        try:
            if col not in df.columns:
                return default
            v = df[col].iloc[-1]
            if pd.isna(v):
                return default
            return float(v)
        except Exception:
            return default

    def _truthy(self, df: pd.DataFrame, col: str) -> bool:
        try:
            if col not in df.columns:
                return False
            return bool(df[col].iloc[-1])
        except Exception:
            return False

    # ============================
    # ✅ Confirmaciones institucionales
    # ============================
    def _bull_confirm(self, df: pd.DataFrame) -> bool:
        """
        BUY institucional: tendencia + momentum + fuerza + volumen
        """
        close = self._getf(df, "close", None)
        ema20 = self._getf(df, "ema20", self._getf(df, "ema_20", None))
        ema50 = self._getf(df, "ema50", self._getf(df, "ema_50", None))
        rsi = self._getf(df, "rsi", 50.0)
        adx = self._getf(df, "adx", 0.0)
        macd = self._getf(df, "macd", 0.0)
        macd_signal = self._getf(df, "macd_signal", 0.0)
        macd_hist = self._getf(df, "macd_hist", 0.0)
        vol_ratio = self._getf(df, "vol_ratio", 1.0)
        vwap = self._getf(df, "vwap", None)

        if close is None or ema20 is None or ema50 is None:
            return False

        # Tendencia base
        trend_ok = (close > ema50) and (ema20 > ema50)

        # Momentum
        rsi_ok = rsi >= 55

        # Fuerza tendencia
        adx_ok = adx >= 18

        # MACD confirmación (hist positivo o cruce)
        macd_ok = (macd > macd_signal) or (macd_hist > 0)

        # Volumen institucional (evita fakeouts)
        vol_ok = vol_ratio >= 1.05

        # VWAP confirmación (si existe)
        vwap_ok = True
        if vwap is not None:
            vwap_ok = close >= vwap

        return bool(trend_ok and rsi_ok and adx_ok and macd_ok and vol_ok and vwap_ok)

    def _bear_confirm(self, df: pd.DataFrame) -> bool:
        """
        SELL institucional: tendencia bajista + momentum bajista + fuerza + volumen
        """
        close = self._getf(df, "close", None)
        ema20 = self._getf(df, "ema20", self._getf(df, "ema_20", None))
        ema50 = self._getf(df, "ema50", self._getf(df, "ema_50", None))
        rsi = self._getf(df, "rsi", 50.0)
        adx = self._getf(df, "adx", 0.0)
        macd = self._getf(df, "macd", 0.0)
        macd_signal = self._getf(df, "macd_signal", 0.0)
        macd_hist = self._getf(df, "macd_hist", 0.0)
        vol_ratio = self._getf(df, "vol_ratio", 1.0)
        vwap = self._getf(df, "vwap", None)

        if close is None or ema20 is None or ema50 is None:
            return False

        # Tendencia base
        trend_ok = (close < ema50) and (ema20 < ema50)

        # Momentum
        rsi_ok = rsi <= 45

        # Fuerza tendencia
        adx_ok = adx >= 18

        # MACD confirmación
        macd_ok = (macd < macd_signal) or (macd_hist < 0)

        # Volumen institucional
        vol_ok = vol_ratio >= 1.05

        # VWAP confirmación
        vwap_ok = True
        if vwap is not None:
            vwap_ok = close <= vwap

        return bool(trend_ok and rsi_ok and adx_ok and macd_ok and vol_ok and vwap_ok)

    # ============================
    # ✅ Main
    # ============================
    def generate(self, df: pd.DataFrame) -> dict:
        # ----------------------------
        # Validaciones base
        # ----------------------------
        if df is None or df.empty:
            return self._hold_response(
                reason="no_market_data",
                probability=0.0,
                price=None,
                df=df,
                regime=None,
            )

        if "close" not in df.columns:
            return self._hold_response(
                reason="missing_close",
                probability=0.0,
                price=None,
                df=df,
                regime=None,
            )

        # ----------------------------
        # Features ML
        # ----------------------------
        model_features = list(self.model.feature_columns)
        available_features = [f for f in model_features if f in df.columns]

        price = float(df["close"].iloc[-1])

        if not available_features:
            return self._hold_response(
                reason="no_usable_features",
                probability=0.0,
                price=price,
                df=df,
                regime=None,
            )

        X = df.tail(1)[available_features]

        # ----------------------------
        # Probabilidad
        # ----------------------------
        try:
            proba_raw = self.model.predict_proba(X)
            if hasattr(proba_raw, "shape"):
                prob = float(proba_raw[0][1])
            else:
                prob = float(proba_raw)
        except Exception:
            return self._hold_response(
                reason="model_predict_failed",
                probability=0.0,
                price=price,
                df=df,
                regime=None,
            )

        # ----------------------------
        # Régimen (IA)
        # ----------------------------
        threshold = float(self.threshold)
        regime = None

        if detect_regime is not None:
            try:
                regime = detect_regime(df)

                # rango: más estricto
                if MarketRegime is not None and regime == MarketRegime.RANGE:
                    threshold += 0.08

                # dead: HOLD directo
                if MarketRegime is not None and regime == MarketRegime.DEAD:
                    return self._hold_response(
                        reason="dead_market",
                        probability=prob,
                        price=price,
                        df=df,
                        regime=regime,
                    )
            except Exception:
                regime = None

        # ----------------------------
        # Institucional: régimen manda
        # ----------------------------
        allow_buy = True
        allow_sell = True

        try:
            if MarketRegime is not None and regime is not None:
                if regime == MarketRegime.BULL:
                    allow_sell = False
                    threshold += 0.02

                if regime == MarketRegime.BEAR:
                    allow_buy = False
                    threshold += 0.02

                if regime == MarketRegime.RANGE:
                    # en rango: casi HOLD
                    allow_sell = False
        except Exception:
            pass

        # ----------------------------
        # Decisión
        # ----------------------------
        buy_threshold = float(threshold)

        signal = None

        # ✅ BUY institucional
        if allow_buy and prob >= buy_threshold and self._bull_confirm(df):
            signal = SignalType.BUY

        # ✅ SELL institucional (NO depende de prob baja)
        elif allow_sell and self._bear_confirm(df):
            signal = SignalType.SELL

        else:
            return self._hold_response(
                reason="filtered_by_institutional_rules",
                probability=prob,
                price=price,
                df=df,
                regime=regime,
            )

        # ----------------------------
        # Gestión de riesgo
        # ----------------------------
        stop_loss = compute_stop_loss(df, signal)
        take_profit = compute_take_profit(price, stop_loss, signal)

        return {
            "signal": signal.value,
            "entry": price,
            "stop": stop_loss,
            "take_profit": take_profit,
            "probability": prob,
            "regime": regime.value if regime else None,
        }

    def _hold_response(
        self,
        reason: str,
        probability: float,
        price: float | None,
        df: pd.DataFrame,
        regime=None,
    ) -> dict:

        stop_loss = None
        take_profit = None

        if price is not None and df is not None and not df.empty:
            stop_loss = compute_stop_loss(df, SignalType.HOLD)
            take_profit = compute_take_profit(price, stop_loss, SignalType.HOLD)

        return {
            "signal": SignalType.HOLD.value,
            "reason": reason,
            "entry": price,
            "stop": stop_loss,
            "take_profit": take_profit,
            "probability": probability,
            "regime": regime.value if regime else None,
        }


# Wrapper compatibilidad
def generate_signal(df: pd.DataFrame, threshold: float = 0.55) -> dict:
    engine = SignalEngine(threshold=threshold)
    return engine.generate(df)
