import React, { useState } from 'react';
import { Shield, TrendingUp, Zap, AlertTriangle, ChevronRight, DollarSign } from 'lucide-react';

export default function AssetAllocationStrategy() {
  const [selectedTier, setSelectedTier] = useState(null);

  const tiers = [
    {
      id: 1,
      name: 'Foundation Layer',
      allocation: '50%',
      risk: 'Low',
      assets: ['BTC', 'ETH', 'SOL'],
      icon: Shield,
      color: 'blue',
      volatility: '30-50% annualized',
      strategies: [
        'Mean reversion on dips',
        'DCA during market panic',
        'Staking rewards (4-8% APY)',
        'Covered calls for income'
      ],
      purpose: 'Capital preservation + steady growth',
      targetReturn: '5-8% monthly',
      advantages: [
        'High liquidity (can exit anytime)',
        'Established price discovery',
        'Less manipulation risk',
        'Predicable volatility patterns'
      ],
      disadvantages: [
        'Lower upside potential',
        'More efficient market (harder edge)',
        'Requires larger capital for meaningful gains'
      ]
    },
    {
      id: 2,
      name: 'Growth Layer',
      allocation: '30%',
      risk: 'Medium',
      assets: ['Top 20-100 altcoins', 'DeFi blue chips', 'Gaming tokens'],
      icon: TrendingUp,
      color: 'green',
      volatility: '100-200% annualized',
      strategies: [
        'Momentum trades on narratives',
        'Swing trade oversold conditions',
        'Event-driven (protocol launches)',
        'Sector rotation'
      ],
      purpose: 'Growth acceleration',
      targetReturn: '10-20% monthly',
      advantages: [
        'Better risk-reward than BTC/ETH',
        'Sector trends more predictable',
        'Sufficient liquidity for entry/exit',
        'Fundamental analysis possible'
      ],
      disadvantages: [
        'Higher correlation in downturns',
        'Requires deeper research',
        'Project risk (team, tech, tokenomics)'
      ]
    },
    {
      id: 3,
      name: 'Opportunity Layer',
      allocation: '20%',
      risk: 'High',
      assets: ['High-quality memecoins', 'New listings', 'Micro-caps'],
      icon: Zap,
      color: 'purple',
      volatility: '500%+ annualized',
      strategies: [
        'Early entry on viral narratives',
        'Quick scalps (15-30min holds)',
        'Momentum breakouts',
        'Social sentiment trading'
      ],
      purpose: 'Asymmetric upside',
      targetReturn: '50%+ on winners (but expect 50% loss rate)',
      advantages: [
        'Massive upside potential (10-100x)',
        'First-mover advantage',
        'AI excels at pattern recognition',
        'Rapid feedback loop for learning'
      ],
      disadvantages: [
        'Extreme scam risk',
        'Low liquidity (slippage)',
        'Sentiment-driven (hard to predict)',
        'Most go to zero'
      ]
    }
  ];

  const memeSpecificRules = [
    {
      rule: 'Never Hold Long-Term',
      detail: 'Exit within 24-72 hours max. Memecoins have no floor.',
      icon: AlertTriangle,
      critical: true
    },
    {
      rule: 'Liquidity First',
      detail: 'Only trade memes with >$100k daily volume. Check if liquidity is locked.',
      icon: DollarSign,
      critical: true
    },
    {
      rule: 'Take Profits Aggressively',
      detail: 'Sell 50% at 2x, 30% at 5x, let 20% ride. Lock in gains early.',
      icon: TrendingUp,
      critical: false
    },
    {
      rule: 'Social Signal Filtering',
      detail: 'AI monitors Twitter, Telegram, Discord. Look for organic growth, not coordinated pumps.',
      icon: Zap,
      critical: false
    },
    {
      rule: 'Contract Analysis Required',
      detail: 'Auto-check for honeypots, mint functions, excessive tax, ownership concentration.',
      icon: Shield,
      critical: true
    }
  ];

  const comparisonMetrics = [
    { metric: 'AI Edge Opportunity', blue: 3, green: 7, purple: 9 },
    { metric: 'Capital Safety', blue: 9, green: 6, purple: 2 },
    { metric: 'Liquidity', blue: 10, green: 8, purple: 3 },
    { metric: 'Upside Potential', blue: 3, green: 6, purple: 10 },
    { metric: 'Time to Profit', blue: 5, green: 7, purple: 9 }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-12">
          <h1 className="text-4xl font-bold mb-4">
            Multi-Tier Asset Strategy
          </h1>
          <p className="text-slate-400 text-lg">
            Don't choose between safety and opportunity—use both strategically
          </p>
        </header>

        {/* Core Philosophy */}
        <div className="bg-gradient-to-r from-blue-900/30 to-purple-900/30 border border-blue-500/30 rounded-lg p-6 mb-8">
          <h2 className="text-2xl font-bold mb-4">The Answer: Hybrid Allocation</h2>
          <p className="text-slate-300 mb-4">
            <strong className="text-green-400">Memecoins can boost returns</strong>, but only as a small, 
            controlled allocation. Use blue-chips as your foundation, then layer in higher-risk plays 
            with strict position limits.
          </p>
          <div className="bg-slate-900/50 p-4 rounded">
            <p className="text-sm text-slate-400">
              Think of it like venture capital: VCs don't bet everything on moonshots. They have a 
              diversified portfolio where 80% returns 1-2x and 20% might 10x. Same principle here.
            </p>
          </div>
        </div>

        {/* Three Tiers */}
        <div className="grid gap-6 mb-12">
          {tiers.map((tier) => {
            const Icon = tier.icon;
            const isSelected = selectedTier === tier.id;
            
            return (
              <div 
                key={tier.id}
                className={`bg-slate-800 border rounded-lg overflow-hidden transition-all cursor-pointer ${
                  isSelected 
                    ? `border-${tier.color}-500` 
                    : 'border-slate-700 hover:border-slate-600'
                }`}
                onClick={() => setSelectedTier(isSelected ? null : tier.id)}
              >
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-4">
                      <div className={`bg-${tier.color}-500/20 p-3 rounded-lg`}>
                        <Icon size={28} className={`text-${tier.color}-400`} />
                      </div>
                      <div>
                        <h3 className="text-2xl font-bold mb-1">{tier.name}</h3>
                        <p className="text-slate-400">{tier.purpose}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-3xl font-bold mb-1">{tier.allocation}</div>
                      <span className={`px-3 py-1 rounded text-sm font-semibold ${
                        tier.risk === 'Low' ? 'bg-green-900 text-green-300' :
                        tier.risk === 'Medium' ? 'bg-yellow-900 text-yellow-300' :
                        'bg-red-900 text-red-300'
                      }`}>
                        {tier.risk} Risk
                      </span>
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-slate-500 mb-2">Assets</p>
                      <div className="flex flex-wrap gap-2">
                        {tier.assets.map((asset, idx) => (
                          <span key={idx} className="px-3 py-1 bg-slate-700 rounded text-sm">
                            {asset}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <p className="text-sm text-slate-500 mb-2">Target Return</p>
                      <p className="text-lg font-semibold text-green-400">{tier.targetReturn}</p>
                      <p className="text-xs text-slate-500">Volatility: {tier.volatility}</p>
                    </div>
                  </div>

                  {isSelected && (
                    <div className="mt-6 pt-6 border-t border-slate-700 space-y-6">
                      <div>
                        <h4 className="font-semibold mb-3 text-lg">Strategies</h4>
                        <ul className="space-y-2">
                          {tier.strategies.map((strategy, idx) => (
                            <li key={idx} className="flex items-start gap-2 text-slate-300">
                              <ChevronRight size={16} className={`mt-1 text-${tier.color}-400 flex-shrink-0`} />
                              <span>{strategy}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div className="grid md:grid-cols-2 gap-4">
                        <div>
                          <h4 className="font-semibold mb-3 text-green-400">Advantages</h4>
                          <ul className="space-y-2 text-sm">
                            {tier.advantages.map((adv, idx) => (
                              <li key={idx} className="text-slate-400">• {adv}</li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <h4 className="font-semibold mb-3 text-red-400">Disadvantages</h4>
                          <ul className="space-y-2 text-sm">
                            {tier.disadvantages.map((dis, idx) => (
                              <li key={idx} className="text-slate-400">• {dis}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Comparison Matrix */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 mb-8">
          <h2 className="text-2xl font-bold mb-6">Performance Comparison Matrix</h2>
          <div className="space-y-4">
            {comparisonMetrics.map((metric, idx) => (
              <div key={idx}>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-slate-300 font-medium">{metric.metric}</span>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <Shield size={14} className="text-blue-400" />
                      <span className="text-xs text-slate-500">Foundation</span>
                    </div>
                    <div className="h-2 bg-slate-700 rounded overflow-hidden">
                      <div 
                        className="h-full bg-blue-500 transition-all"
                        style={{ width: `${metric.blue * 10}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <TrendingUp size={14} className="text-green-400" />
                      <span className="text-xs text-slate-500">Growth</span>
                    </div>
                    <div className="h-2 bg-slate-700 rounded overflow-hidden">
                      <div 
                        className="h-full bg-green-500 transition-all"
                        style={{ width: `${metric.green * 10}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <Zap size={14} className="text-purple-400" />
                      <span className="text-xs text-slate-500">Opportunity</span>
                    </div>
                    <div className="h-2 bg-slate-700 rounded overflow-hidden">
                      <div 
                        className="h-full bg-purple-500 transition-all"
                        style={{ width: `${metric.purple * 10}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Memecoin-Specific Rules */}
        <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-3">
            <AlertTriangle className="text-red-400" />
            Critical Rules for Memecoin Trading
          </h2>
          <p className="text-slate-300 mb-6">
            If you allocate to memecoins, your AI MUST enforce these rules. No exceptions.
          </p>
          <div className="grid md:grid-cols-2 gap-4">
            {memeSpecificRules.map((rule, idx) => {
              const RuleIcon = rule.icon;
              return (
                <div 
                  key={idx}
                  className={`p-4 rounded-lg ${
                    rule.critical 
                      ? 'bg-red-900/30 border border-red-500/50' 
                      : 'bg-slate-800 border border-slate-700'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <RuleIcon size={20} className={rule.critical ? 'text-red-400' : 'text-slate-400'} />
                    <div>
                      <h4 className="font-bold mb-1">
                        {rule.rule}
                        {rule.critical && <span className="text-red-400 ml-2">*CRITICAL*</span>}
                      </h4>
                      <p className="text-sm text-slate-400">{rule.detail}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Final Recommendation */}
        <div className="mt-8 bg-gradient-to-r from-green-900/30 to-blue-900/30 border border-green-500/30 rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-4">Bottom Line</h2>
          <div className="space-y-3 text-slate-300">
            <p className="flex items-start gap-2">
              <span className="text-green-400 font-bold">✓</span>
              <span><strong>Start with 50% blue-chips</strong> to build consistent, safe returns</span>
            </p>
            <p className="flex items-start gap-2">
              <span className="text-green-400 font-bold">✓</span>
              <span><strong>Add 30% mid-caps</strong> once your foundation is profitable for 2+ weeks</span>
            </p>
            <p className="flex items-start gap-2">
              <span className="text-green-400 font-bold">✓</span>
              <span><strong>Layer in 20% memecoins</strong> only after your AI proves it can manage risk</span>
            </p>
            <p className="flex items-start gap-2">
              <span className="text-yellow-400 font-bold">!</span>
              <span>Treat memecoins like lottery tickets: small bets, massive upside, expect losses</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}