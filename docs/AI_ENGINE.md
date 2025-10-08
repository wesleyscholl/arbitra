# AI Engine Documentation

## Overview

The Arbitra AI Engine uses **Google Gemini** for intelligent trading analysis and decision-making. The system provides:

- **Fast Analysis**: Gemini 2.0 Flash for real-time decisions (<2s response)
- **Deep Analysis**: Gemini 1.5 Pro for complex market conditions (<5s response)
- **Confidence Scoring**: Calibrated confidence scores based on historical accuracy
- **Trade Memory**: Pattern recognition using vector similarity search

## Why Gemini?

We chose Google Gemini over Anthropic Claude and OpenAI GPT for several reasons:

1. **Cost-Effective**: More affordable API pricing for high-volume trading analysis
2. **Speed**: Gemini 2.0 Flash provides near-instant responses for time-sensitive decisions
3. **Versatility**: Dual-model approach (Flash for speed, Pro for depth)
4. **JSON Mode**: Native support for structured outputs
5. **Context Window**: Large context windows for comprehensive market analysis

## Architecture

```
┌─────────────────────────────────────────────────┐
│              AI Trading Engine                  │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐      ┌──────────────┐        │
│  │ Trading Agent│      │  Confidence  │        │
│  │              │      │    Scorer    │        │
│  │ • Gemini API │──────│ • Calibration│        │
│  │ • Flash/Pro  │      │ • Tracking   │        │
│  └──────────────┘      └──────────────┘        │
│         │                       │              │
│         └───────────┬───────────┘              │
│                     │                          │
│              ┌──────────────┐                  │
│              │ Trade Memory │                  │
│              │              │                  │
│              │ • Pinecone   │                  │
│              │ • Embeddings │                  │
│              │ • Patterns   │                  │
│              └──────────────┘                  │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Setup

### 1. Get API Keys

#### Google Gemini API
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Get API Key"
3. Copy your API key

#### Pinecone
1. Sign up at [Pinecone](https://www.pinecone.io/)
2. Create a new project
3. Get your API key and environment from the dashboard

### 2. Configure Environment

Copy the example configuration:
```bash
cp config/ai.env.example config/ai.env
```

Edit `config/ai.env` with your API keys:
```bash
GEMINI_API_KEY=your_actual_gemini_api_key
PINECONE_API_KEY=your_actual_pinecone_key
PINECONE_ENVIRONMENT=us-west-2-aws
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `google-generativeai`: Google Gemini Python SDK
- `pinecone-client`: Pinecone vector database client

## Usage

### Basic Trade Analysis

```python
from src.ai import TradingAgent, AnalysisRequest
from decimal import Decimal

# Initialize agent
agent = TradingAgent(api_key="your_gemini_api_key")

# Create analysis request
request = AnalysisRequest(
    symbol="SOL",
    current_price=Decimal("98.50"),
    market_data={
        "volume_24h": 1500000000,
        "market_cap": 45000000000,
        "price_change_24h": 5.2
    },
    technical_indicators={
        "rsi": 62,
        "macd": 0.45,
        "bb_position": 0.7  # Bollinger Band position
    },
    sentiment_data={
        "twitter_sentiment": 0.75,
        "reddit_sentiment": 0.68
    }
)

# Get analysis (fast)
analysis = agent.analyze_trade(request)

print(f"Action: {analysis.action}")
print(f"Confidence: {analysis.confidence:.2%}")
print(f"Reasoning: {analysis.reasoning}")

# Use deep analysis for complex decisions
deep_analysis = agent.analyze_trade(request, use_deep_analysis=True)
```

### Confidence Scoring

```python
from src.ai import ConfidenceScorer, ConfidenceFactors
from decimal import Decimal

# Initialize scorer
scorer = ConfidenceScorer()

# Define factors
factors = ConfidenceFactors(
    technical_score=Decimal("0.85"),
    sentiment_score=Decimal("0.72"),
    liquidity_score=Decimal("0.90"),
    risk_reward_score=Decimal("0.80"),
    historical_accuracy=Decimal("0.65")
)

# Calculate calibrated confidence
confidence = scorer.calculate_confidence(factors, asset_tier="FOUNDATION")
print(f"Calibrated confidence: {confidence:.2%}")

# Record outcome for calibration
scorer.record_outcome(
    predicted_confidence=Decimal("0.85"),
    actual_success=True,
    profit_loss_pct=Decimal("0.08")  # 8% profit
)

# Get calibration metrics
metrics = scorer.get_calibration_metrics()
print(f"Overall success rate: {metrics['overall_success_rate']:.2%}")
print(f"Brier score: {metrics['brier_score']:.3f}")
```

### Trade Memory

```python
from src.ai import TradeMemory, TradePattern
from datetime import datetime
from decimal import Decimal

# Initialize memory
memory = TradeMemory(
    api_key="your_pinecone_key",
    environment="us-west-2-aws"
)

# Store a trade
pattern = TradePattern(
    trade_id="trade_001",
    symbol="SOL",
    entry_price=Decimal("98.50"),
    action="BUY",
    confidence=Decimal("0.85"),
    reasoning="Strong bullish momentum with RSI confirmation",
    timestamp=datetime.now(),
    rsi=Decimal("62"),
    volume_24h=Decimal("1500000000"),
    sentiment_score=Decimal("0.75")
)

# Create embedding (you would use a proper embedding model)
from src.ai.memory import create_embedding_from_conditions
embedding = create_embedding_from_conditions(
    symbol="SOL",
    rsi=Decimal("62"),
    volume_24h=Decimal("1500000000"),
    sentiment_score=Decimal("0.75"),
    reasoning=pattern.reasoning
)

memory.store_trade(pattern, embedding)

# Find similar trades
similar = memory.find_similar_trades(
    query_embedding=embedding,
    symbol="SOL",
    limit=10
)

for trade in similar:
    print(f"{trade.symbol}: {trade.action} @ ${trade.entry_price} "
          f"(confidence: {trade.confidence:.2%})")

# Update with outcome
memory.update_trade_outcome(
    trade_id="trade_001",
    exit_price=Decimal("106.50"),
    profit_loss_pct=Decimal("0.0812"),  # 8.12% profit
    success=True,
    max_drawdown=Decimal("0.02"),  # 2% max drawdown
    holding_period_hours=48
)
```

### Batch Analysis

```python
# Analyze multiple assets at once
requests = [
    AnalysisRequest(symbol="BTC", current_price=Decimal("42000"), ...),
    AnalysisRequest(symbol="ETH", current_price=Decimal("2200"), ...),
    AnalysisRequest(symbol="SOL", current_price=Decimal("98.50"), ...)
]

# Get analyses
analyses = agent.batch_analyze(requests)

for req, analysis in zip(requests, analyses):
    print(f"{req.symbol}: {analysis.action} ({analysis.confidence:.2%})")
```

## Model Selection

The AI Engine uses two Gemini models:

### Gemini 2.0 Flash (Default)
- **Use For**: Real-time analysis, quick decisions, portfolio scanning
- **Speed**: <2 seconds typical response
- **Cost**: More cost-effective for high-volume
- **Best For**: Foundation and Growth tier assets

### Gemini 1.5 Pro (Optional)
- **Use For**: Complex market conditions, high-stakes decisions, opportunity tier
- **Speed**: <5 seconds typical response
- **Cost**: Higher but more sophisticated
- **Best For**: Opportunity tier (memecoins), unusual market conditions

Set `use_deep_analysis=True` to use the Pro model:
```python
analysis = agent.analyze_trade(request, use_deep_analysis=True)
```

## Prompt Engineering

The AI Engine uses carefully crafted prompts that include:

1. **Market Context**: Current price, volume, market cap
2. **Technical Indicators**: RSI, MACD, Bollinger Bands
3. **Sentiment Data**: Social media sentiment scores
4. **On-Chain Metrics**: Holder distribution, liquidity
5. **Risk Rules**: Tier-specific position limits and risk tolerances
6. **Portfolio Context**: Current holdings and diversification needs

### Example Output Format

```json
{
    "action": "BUY",
    "confidence": 0.85,
    "entry_price": 98.50,
    "take_profit": 106.00,
    "stop_loss": 95.00,
    "reasoning": "SOL showing strong momentum with RSI at 62 (not overbought)...",
    "risk_factors": [
        "General market volatility",
        "High correlation with BTC movements"
    ],
    "opportunity_factors": [
        "Strong developer activity",
        "Increasing network usage",
        "Positive sentiment across social channels"
    ],
    "time_horizon": "medium"
}
```

## Confidence Calibration

The confidence scoring system automatically calibrates based on historical accuracy:

1. **Tracks Outcomes**: Records predicted confidence vs. actual results
2. **Bins Confidence**: Divides confidence into 10 bins (0-10%, 10-20%, etc.)
3. **Calibrates**: Adjusts future predictions based on historical accuracy per bin
4. **Metrics**: Provides Brier score and bin-level statistics

A well-calibrated system should have:
- Brier score < 0.2
- Actual success rates matching predicted confidence per bin
- Minimum 20 samples before applying calibration

## Performance Benchmarks

Target performance metrics:

| Metric | Target | Current |
|--------|--------|---------|
| Response Time (Flash) | <2s | TBD |
| Response Time (Pro) | <5s | TBD |
| Confidence Correlation (R²) | >0.6 | TBD |
| Pattern Retrieval | <500ms | TBD |
| Brier Score | <0.2 | TBD |

## Error Handling

The AI Engine includes robust error handling:

- **API Failures**: Returns safe default (HOLD with 0% confidence)
- **Parse Errors**: Defaults to HOLD for safety
- **Rate Limits**: Implements exponential backoff
- **Validation**: Ensures all outputs meet schema requirements

## Testing

Run the AI Engine tests:
```bash
pytest tests/ai/ -v --cov=src/ai
```

Test coverage target: **95%+**

## Cost Optimization

Tips for managing API costs:

1. **Use Flash by Default**: Reserve Pro model for complex situations
2. **Batch Requests**: Use `batch_analyze()` when possible
3. **Cache Results**: Store recent analyses to avoid redundant calls
4. **Confidence Threshold**: Skip AI analysis for very low/high confidence signals
5. **Monitor Usage**: Track API calls and costs in logs

## Security

- **Never commit API keys**: Use environment variables
- **Rotate keys regularly**: Change API keys every 90 days
- **Monitor access**: Check for unusual API usage patterns
- **Rate limiting**: Implement client-side rate limits
- **Audit logs**: Log all AI decisions for review

## Troubleshooting

### Import Error
```
ModuleNotFoundError: No module named 'google.generativeai'
```
Solution: `pip install google-generativeai`

### API Key Error
```
google.api_core.exceptions.PermissionDenied: API key not valid
```
Solution: Check your `GEMINI_API_KEY` in `config/ai.env`

### Pinecone Connection Error
```
pinecone.core.client.exceptions.NotFoundException
```
Solution: Verify `PINECONE_ENVIRONMENT` and index exists

### Slow Responses
- Check network latency to Google AI servers
- Consider using Flash model instead of Pro
- Reduce `max_tokens` in configuration

## Next Steps

- [ ] Implement sentence-transformers for better embeddings
- [ ] Add multi-language support for global markets
- [ ] Implement A/B testing for prompt variations
- [ ] Add real-time learning from live trades
- [ ] Integrate with portfolio optimizer

## References

- [Google Gemini Documentation](https://ai.google.dev/docs)
- [Pinecone Documentation](https://docs.pinecone.io/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
