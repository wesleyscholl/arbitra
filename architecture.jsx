import React, { useState } from 'react';
import { Shield, TrendingUp, Brain, Database, AlertTriangle, Activity, Settings, BarChart3 } from 'lucide-react';

export default function CryptoAgentArchitecture() {
  const [activeTab, setActiveTab] = useState('overview');

  const architectureLayers = [
    {
      name: 'Risk Management Layer',
      icon: Shield,
      color: 'bg-red-500',
      components: [
        'Position sizing (Kelly Criterion)',
        'Stop-loss automation',
        'Drawdown limits (5-10% max)',
        'Portfolio heat monitoring',
        'Correlation analysis'
      ]
    },
    {
      name: 'Decision Engine',
      icon: Brain,
      color: 'bg-blue-500',
      components: [
        'LLM reasoning (GPT-4/Claude)',
        'Multi-timeframe analysis',
        'Sentiment scoring',
        'Pattern recognition',
        'Confidence scoring'
      ]
    },
    {
      name: 'Data Intelligence',
      icon: Database,
      color: 'bg-green-500',
      components: [
        'On-chain metrics (Dune, Nansen)',
        'Order book depth',
        'Whale wallet tracking',
        'Smart money flows',
        'Token health scores'
      ]
    },
    {
      name: 'Execution Layer',
      icon: Activity,
      color: 'bg-purple-500',
      components: [
        'Jupiter aggregator API',
        'Slippage protection',
        'Gas optimization',
        'Order splitting',
        'Failed transaction handling'
      ]
    }
  ];

  const strategies = [
    {
      name: 'Mean Reversion',
      risk: 'Low',
      timeframe: '1-7 days',
      description: 'Buy oversold blue-chips (SOL, ETH, BTC) when RSI < 30, sell when normalized',
      capitalAllocation: '40%'
    },
    {
      name: 'Momentum Scalping',
      risk: 'Medium',
      timeframe: '15min-4hr',
      description: 'Ride established trends with tight stops, 2:1 risk-reward minimum',
      capitalAllocation: '30%'
    },
    {
      name: 'Arbitrage',
      risk: 'Very Low',
      timeframe: 'Seconds-Minutes',
      description: 'CEX-DEX price differences, cross-chain opportunities',
      capitalAllocation: '20%'
    },
    {
      name: 'Yield Farming',
      risk: 'Low',
      timeframe: 'Days-Weeks',
      description: 'Stable LP pairs, audited protocols only, auto-compound',
      capitalAllocation: '10%'
    }
  ];

  const keyPrinciples = [
    {
      title: 'Capital Preservation First',
      description: 'Never risk more than 1-2% per trade. System shuts down if daily loss exceeds 3%.',
      icon: Shield
    },
    {
      title: 'Diversification',
      description: 'Never more than 10% in a single position. Mix of strategies and assets.',
      icon: BarChart3
    },
    {
      title: 'Asymmetric Risk-Reward',
      description: 'Target minimum 2:1 reward-to-risk. Skip trades that don\'t meet criteria.',
      icon: TrendingUp
    },
    {
      title: 'Continuous Learning',
      description: 'Log all trades, analyze losses, retrain models monthly with new data.',
      icon: Brain
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-12">
          <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            Capital-Preserving AI Trading Agent
          </h1>
          <p className="text-slate-400 text-lg">
            Architecture for steady profits with risk-first approach
          </p>
        </header>

        {/* Navigation */}
        <div className="flex gap-4 mb-8 border-b border-slate-700">
          {['overview', 'architecture', 'strategies', 'implementation'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 px-4 capitalize transition-colors ${
                activeTab === tab
                  ? 'border-b-2 border-blue-400 text-blue-400'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-3">
                <AlertTriangle className="text-yellow-400" />
                Core Philosophy
              </h2>
              <p className="text-slate-300 mb-4">
                This system prioritizes <span className="text-green-400 font-semibold">not losing money</span> over 
                making spectacular gains. Target: 5-15% monthly returns with maximum 10% drawdown.
              </p>
              <div className="bg-slate-900 p-4 rounded border border-slate-600">
                <p className="text-sm text-slate-400 italic">
                  "Compound 8% monthly = 2.5x your capital in a year. Consistency beats lottery tickets."
                </p>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              {keyPrinciples.map((principle, idx) => (
                <div key={idx} className="bg-slate-800 border border-slate-700 rounded-lg p-6">
                  <div className="flex items-start gap-4">
                    <principle.icon className="text-blue-400 flex-shrink-0" size={28} />
                    <div>
                      <h3 className="text-xl font-semibold mb-2">{principle.title}</h3>
                      <p className="text-slate-400">{principle.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Architecture Tab */}
        {activeTab === 'architecture' && (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-blue-900/30 to-purple-900/30 border border-blue-500/30 rounded-lg p-6">
              <h2 className="text-2xl font-bold mb-4">System Layers (Bottom-Up)</h2>
              <p className="text-slate-300">
                Each layer has veto power. If Risk Management says no, the trade doesn't happen—regardless 
                of how confident the AI is.
              </p>
            </div>

            <div className="grid gap-6">
              {architectureLayers.map((layer, idx) => (
                <div key={idx} className="bg-slate-800 border border-slate-700 rounded-lg p-6">
                  <div className="flex items-center gap-4 mb-4">
                    <div className={`${layer.color} p-3 rounded-lg`}>
                      <layer.icon size={24} />
                    </div>
                    <h3 className="text-xl font-bold">{layer.name}</h3>
                  </div>
                  <ul className="space-y-2">
                    {layer.components.map((component, cidx) => (
                      <li key={cidx} className="flex items-center gap-3">
                        <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                        <span className="text-slate-300">{component}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Strategies Tab */}
        {activeTab === 'strategies' && (
          <div className="space-y-6">
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <h2 className="text-2xl font-bold mb-4">Multi-Strategy Portfolio</h2>
              <p className="text-slate-300 mb-4">
                Don't put all eggs in one basket. Different strategies perform in different market conditions.
              </p>
            </div>

            <div className="grid gap-4">
              {strategies.map((strategy, idx) => (
                <div key={idx} className="bg-slate-800 border border-slate-700 rounded-lg p-6 hover:border-blue-500/50 transition-colors">
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="text-xl font-bold">{strategy.name}</h3>
                    <div className="flex gap-3">
                      <span className={`px-3 py-1 rounded text-sm font-semibold ${
                        strategy.risk === 'Very Low' ? 'bg-green-900 text-green-300' :
                        strategy.risk === 'Low' ? 'bg-green-800 text-green-300' :
                        'bg-yellow-800 text-yellow-300'
                      }`}>
                        {strategy.risk} Risk
                      </span>
                      <span className="px-3 py-1 rounded text-sm font-semibold bg-blue-900 text-blue-300">
                        {strategy.capitalAllocation}
                      </span>
                    </div>
                  </div>
                  <p className="text-slate-400 mb-2">{strategy.description}</p>
                  <p className="text-sm text-slate-500">Timeframe: {strategy.timeframe}</p>
                </div>
              ))}
            </div>

            <div className="bg-amber-900/20 border border-amber-500/30 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-2 flex items-center gap-2">
                <AlertTriangle size={20} className="text-amber-400" />
                Strategy Rotation
              </h3>
              <p className="text-slate-300">
                The AI monitors which strategies are profitable in current market conditions and dynamically 
                adjusts allocation. Bear market? More arbitrage and yield. Bull market? More momentum plays.
              </p>
            </div>
          </div>
        )}

        {/* Implementation Tab */}
        {activeTab === 'implementation' && (
          <div className="space-y-6">
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-3">
                <Settings className="text-purple-400" />
                Technical Stack
              </h2>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
                <h3 className="text-lg font-bold mb-4 text-blue-400">AI & Decision Making</h3>
                <ul className="space-y-3 text-slate-300">
                  <li className="flex gap-2">
                    <span className="text-blue-400">→</span>
                    <span><strong>Claude/GPT-4:</strong> Market analysis, pattern recognition</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-blue-400">→</span>
                    <span><strong>LangChain:</strong> Agent orchestration, memory</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-blue-400">→</span>
                    <span><strong>Vector DB:</strong> Historical trade analysis</span>
                  </li>
                </ul>
              </div>

              <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
                <h3 className="text-lg font-bold mb-4 text-green-400">Data Sources</h3>
                <ul className="space-y-3 text-slate-300">
                  <li className="flex gap-2">
                    <span className="text-green-400">→</span>
                    <span><strong>Helius/QuickNode:</strong> Solana RPC</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-green-400">→</span>
                    <span><strong>Birdeye/DexScreener:</strong> Price feeds, volume</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-green-400">→</span>
                    <span><strong>Dune Analytics:</strong> On-chain metrics</span>
                  </li>
                </ul>
              </div>

              <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
                <h3 className="text-lg font-bold mb-4 text-purple-400">Execution</h3>
                <ul className="space-y-3 text-slate-300">
                  <li className="flex gap-2">
                    <span className="text-purple-400">→</span>
                    <span><strong>Jupiter API:</strong> Best price routing</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-purple-400">→</span>
                    <span><strong>Solana Web3.js:</strong> Transaction signing</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-purple-400">→</span>
                    <span><strong>Jito MEV:</strong> Bundle transactions</span>
                  </li>
                </ul>
              </div>

              <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
                <h3 className="text-lg font-bold mb-4 text-red-400">Risk & Monitoring</h3>
                <ul className="space-y-3 text-slate-300">
                  <li className="flex gap-2">
                    <span className="text-red-400">→</span>
                    <span><strong>TA-Lib:</strong> Technical indicators</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-red-400">→</span>
                    <span><strong>PostgreSQL:</strong> Trade logging</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-red-400">→</span>
                    <span><strong>Grafana:</strong> Real-time dashboards</span>
                  </li>
                </ul>
              </div>
            </div>

            <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Sample Decision Flow</h3>
              <div className="bg-slate-900 p-4 rounded border border-slate-600 font-mono text-sm space-y-2">
                <div className="text-slate-400">1. Scan market for opportunities (every 30s)</div>
                <div className="text-slate-400">2. AI generates trade hypothesis + confidence score</div>
                <div className="text-slate-400">3. Risk layer validates: position size OK? Correlation OK? Heat OK?</div>
                <div className="text-green-400">4. ✓ Approved → Execute via Jupiter with 1% slippage limit</div>
                <div className="text-slate-400">5. Monitor position, update stop-loss based on volatility</div>
                <div className="text-slate-400">6. Take profit at target OR stop out if thesis invalidated</div>
                <div className="text-slate-400">7. Log trade to database, update AI context</div>
              </div>
            </div>

            <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-2 flex items-center gap-2">
                <AlertTriangle size={20} className="text-red-400" />
                Critical Safeguards
              </h3>
              <ul className="space-y-2 text-slate-300">
                <li>• Kill switch accessible via Telegram/Discord (emergency shutdown)</li>
                <li>• Daily loss limit: 3% of portfolio → system pauses for 24hrs</li>
                <li>• No trades during low liquidity hours (2-6am UTC)</li>
                <li>• Manual approval required for trades greater than 5% of portfolio</li>
                <li>• Anomaly detection: halts if behavior deviates from training</li>
              </ul>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="mt-12 pt-8 border-t border-slate-700">
          <p className="text-slate-500 text-sm text-center">
            Remember: Past performance doesn't guarantee future results. Start with small capital, 
            validate strategies in testnet/paper trading, and scale gradually.
          </p>
        </div>
      </div>
    </div>
  );
}