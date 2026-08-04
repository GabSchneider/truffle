import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

FINANCIAL_KEYWORDS = [
    'lucro', 'prejuízo', 'ebitda', 'receita', 'dividendo', 'jcp', 'balanço', 'rating',
    'aquisição', 'fusão', 'recompra', 'guidance', 'recuperação judicial', 'inadimplência',
    'fraude', 'investigação', 'faturamento', 'proventos', 'ações', 'cvm', 'fato relevante'
]

class SentimentAnalyzer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        financial_lexicon_pt = {
            'lucro recorde': 3.0, 'lucro liquido': 2.5, 'lucro líquido': 2.5,
            'alta de dividendos': 2.5, 'pagamento de dividendos': 2.0, 'jcp': 1.8,
            'superou expectativas': 2.5, 'crescimento expressivo': 2.5, 'elevação de rating': 2.5,
            'recompra de ações': 2.0, 'guidance otimista': 2.0, 'valorização': 1.8,
            'ebitda': 1.5, 'expansão': 1.5, 'aquisição estratégica': 2.0, 'superou': 1.5,
            'lucro': 2.0, 'alta': 1.5, 'crescimento': 1.5, 'recorde': 2.0,

            'prejuízo recorde': -3.0, 'prejuízo líquido': -2.5, 'prejuizo liquido': -2.5,
            'corte de dividendos': -2.5, 'rebaixamento de nota': -2.5, 'rebaixamento de rating': -2.5,
            'queda livre': -2.5, 'despenca': -2.5, 'recuperação judicial': -3.0,
            'inadimplência': -2.0, 'calote': -3.0, 'fraude': -3.0, 'investigação': -2.0,
            'prejuízo': -2.0, 'prejuizo': -2.0, 'queda': -1.5, 'crise': -2.0, 'rebaixou': -1.8,
            'multa': -1.8, 'risco fiscal': -2.0, 'cancelamento': -1.5
        }
        self.sia.lexicon.update(financial_lexicon_pt)

    def evaluate_relevance(self, text: str, orig_canal: str) -> str:
        """Avalia se a notícia tem relevância real para o mercado ou se é mero ruído"""
        if orig_canal == 'cvm_oficial':
            return 'alta'
        
        text_lower = text.lower()
        matches = sum(1 for kw in FINANCIAL_KEYWORDS if kw in text_lower)
        
        if matches >= 2:
            return 'alta'
        elif matches == 1:
            return 'media'
        else:
            return 'irrelevante'

    def analyze(self, text: str, fonte_tipo: str = "media", orig_canal: str = "midia_oficial", ticker: str = "") -> dict:
        text_lower = text.lower()
        scores = self.sia.polarity_scores(text_lower)
        compound = scores['compound']

        relevancia = self.evaluate_relevance(text, orig_canal)

        weight = 1.0
        if orig_canal == 'cvm_oficial':
            weight = 2.0
        elif fonte_tipo == 'confiavel':
            weight = 1.25
        elif fonte_tipo == 'gossip':
            weight = 0.75

        # Se for irrelevante (ruído), reduz a força da polaridade
        if relevancia == 'irrelevante':
            weight *= 0.3

        weighted_score = compound * weight

        if weighted_score >= 0.05:
            label = "positivo"
        elif weighted_score <= -0.05:
            label = "negativo"
        else:
            label = "neutro"

        is_alert = abs(weighted_score) >= 0.35

        bullet_1 = f"Análise sobre {ticker}: {text[:75]}..."
        bullet_2 = f"Impacto estimado: {label.upper()} (Relevância: {relevancia.upper()})."
        bullet_3 = f"Origem: {orig_canal.replace('_', ' ').upper()} (Score Ponderado: {round(weighted_score, 2)})."

        return {
            "score": round(weighted_score, 4),
            "label": label,
            "relevancia": relevancia,
            "peso_evento": weight,
            "alerta_fluxo": is_alert,
            "bullet_points": [bullet_1, bullet_2, bullet_3]
        }
