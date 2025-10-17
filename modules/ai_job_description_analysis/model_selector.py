"""
Model Selector - Intelligent Gemini Model Selection
===================================================

Automatically selects the optimal Gemini model based on workload characteristics,
quality requirements, token budgets, and time constraints.

Selection Strategies:
- Workload-based (tier, batch size, complexity)
- Quality-based (auto-switching based on results)
- Budget-based (conserve tokens when running low)
- Time-based (peak hours vs off-peak)
- Hybrid (combines multiple strategies)

Author: Automated Job Application System v4.3.2
Created: 2025-10-12
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ModelTier(Enum):
    """Model performance tiers."""
    LITE = "lite"       # Fastest, lowest quality, lowest cost
    STANDARD = "standard"  # Balanced speed/quality/cost
    PREMIUM = "premium"    # Best quality, higher cost


@dataclass
class ModelSpec:
    """Specification for a Gemini model."""
    model_id: str
    tier: ModelTier
    name: str
    rpm_limit: int  # Requests per minute
    tokens_per_minute: int
    input_cost_per_1k: float  # Cost per 1K input tokens
    output_cost_per_1k: float  # Cost per 1K output tokens
    max_output_tokens: int
    best_for: List[str]


@dataclass
class ModelSelection:
    """Result of model selection with rationale."""
    model_id: str
    model_spec: ModelSpec
    selection_reason: str
    confidence: float  # 0.0-1.0
    alternative_model: Optional[str]
    estimated_cost: float
    estimated_quality: float  # 0.0-1.0


class ModelSelector:
    """
    Intelligent model selection for Gemini API calls.

    This class analyzes workload characteristics and system state to select
    the most appropriate model for each analysis task.
    """

    # Model registry
    MODELS = {
        'gemini-2.0-flash-lite-001': ModelSpec(
            model_id='gemini-2.0-flash-lite-001',
            tier=ModelTier.LITE,
            name='Gemini 2.0 Flash Lite',
            rpm_limit=15,
            tokens_per_minute=32000,
            input_cost_per_1k=0.0,  # Free tier
            output_cost_per_1k=0.0,  # Free tier
            max_output_tokens=8192,
            best_for=['tier2', 'tier3', 'small_batches', 'off_peak']
        ),
        'gemini-2.0-flash-001': ModelSpec(
            model_id='gemini-2.0-flash-001',
            tier=ModelTier.STANDARD,
            name='Gemini 2.0 Flash',
            rpm_limit=15,
            tokens_per_minute=32000,
            input_cost_per_1k=0.0,  # Free tier
            output_cost_per_1k=0.0,  # Free tier
            max_output_tokens=8192,
            best_for=['tier1', 'large_batches', 'peak_hours', 'complex_analysis']
        ),
        'gemini-2.5-flash': ModelSpec(
            model_id='gemini-2.5-flash',
            tier=ModelTier.PREMIUM,
            name='Gemini 2.5 Flash',
            rpm_limit=60,
            tokens_per_minute=128000,
            input_cost_per_1k=0.30,  # Paid tier
            output_cost_per_1k=2.50,  # Paid tier
            max_output_tokens=8192,
            best_for=['tier1', 'high_quality', 'large_scale', 'critical_analysis']
        )
    }

    # Quality thresholds for auto-switching
    QUALITY_THRESHOLDS = {
        'low': 0.75,      # Below this, upgrade model
        'acceptable': 0.85,  # Target quality range
        'excellent': 0.95,   # Above this, can downgrade
    }

    # Token budget thresholds
    BUDGET_THRESHOLDS = {
        'critical': 0.90,  # >90% used, must conserve
        'high': 0.80,      # >80% used, prefer lite
        'moderate': 0.60,  # 60-80% used, balanced
        'low': 0.40,       # <40% used, can use premium
    }

    def __init__(self, default_model: str = 'gemini-2.0-flash-001'):
        """
        Initialize the model selector.

        Args:
            default_model: Default model to use if no clear preference
        """
        self.default_model = default_model
        self.current_model = default_model
        self.model_switches = 0
        self.selection_history = []

        logger.info(f"ModelSelector initialized with default: {default_model}")

    def select_model(
        self,
        tier: str,
        batch_size: int,
        daily_tokens_used: int = 0,
        daily_token_limit: int = 1500000,
        recent_quality_score: Optional[float] = None,
        time_sensitive: bool = False
    ) -> ModelSelection:
        """
        Select optimal model based on multiple factors.

        Args:
            tier: Analysis tier ('tier1', 'tier2', 'tier3')
            batch_size: Number of jobs in batch
            daily_tokens_used: Tokens used today
            daily_token_limit: Daily token limit
            recent_quality_score: Quality score from recent analysis (0.0-1.0)
            time_sensitive: Whether fast response is critical

        Returns:
            ModelSelection with chosen model and rationale
        """
        # Calculate selection scores for each strategy
        workload_score = self._score_by_workload(tier, batch_size)
        budget_score = self._score_by_budget(daily_tokens_used, daily_token_limit)
        quality_score = self._score_by_quality(recent_quality_score, tier)
        time_score = self._score_by_time(time_sensitive)

        # Combine scores with weights
        weights = {
            'workload': 0.4,
            'budget': 0.3,
            'quality': 0.2,
            'time': 0.1
        }

        model_scores = {}
        for model_id in self.MODELS.keys():
            combined_score = (
                workload_score.get(model_id, 0.5) * weights['workload'] +
                budget_score.get(model_id, 0.5) * weights['budget'] +
                quality_score.get(model_id, 0.5) * weights['quality'] +
                time_score.get(model_id, 0.5) * weights['time']
            )
            model_scores[model_id] = combined_score

        # Select highest scoring model
        best_model_id = max(model_scores.items(), key=lambda x: x[1])[0]
        best_score = model_scores[best_model_id]

        # Get second-best as alternative
        sorted_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
        alternative_model = sorted_models[1][0] if len(sorted_models) > 1 else None

        # Build selection rationale
        reason = self._build_selection_reason(
            best_model_id, tier, batch_size,
            daily_tokens_used / daily_token_limit if daily_token_limit > 0 else 0,
            recent_quality_score, time_sensitive
        )

        # Estimate cost and quality
        model_spec = self.MODELS[best_model_id]
        estimated_cost = self._estimate_cost(model_spec, batch_size, tier)
        estimated_quality = self._estimate_quality(model_spec, tier)

        selection = ModelSelection(
            model_id=best_model_id,
            model_spec=model_spec,
            selection_reason=reason,
            confidence=best_score,
            alternative_model=alternative_model,
            estimated_cost=estimated_cost,
            estimated_quality=estimated_quality
        )

        # Track selection history
        self.selection_history.append({
            'timestamp': datetime.now().isoformat(),
            'model': best_model_id,
            'tier': tier,
            'batch_size': batch_size,
            'confidence': best_score,
        })

        # Update current model if changed
        if best_model_id != self.current_model:
            logger.info(f"Model switched: {self.current_model} -> {best_model_id}")
            self.current_model = best_model_id
            self.model_switches += 1

        logger.info(
            f"Selected model: {best_model_id} (confidence: {best_score:.2f}) - {reason}"
        )

        return selection

    def _score_by_workload(self, tier: str, batch_size: int) -> Dict[str, float]:
        """
        Score models based on workload characteristics.

        IMPORTANT: Tier 2/3 require MORE sophisticated reasoning (strategic thinking,
        nuanced analysis) than Tier 1 (structured data extraction). Therefore,
        higher tiers should prefer more capable models, not lite models.

        Tier Complexity:
        - Tier 1: Structured data extraction (skills, industry, compensation)
                  -> Standard model sufficient
        - Tier 2: Nuanced reasoning (stress analysis, red flags, implicit requirements)
                  -> Prefer standard or premium models
        - Tier 3: Strategic thinking (prestige assessment, positioning, pain points)
                  -> Prefer premium models for best reasoning

        Args:
            tier: Analysis tier
            batch_size: Number of jobs

        Returns:
            Dict of {model_id: score} where score is 0.0-1.0
        """
        scores = {}

        for model_id, spec in self.MODELS.items():
            score = 0.5  # Neutral baseline

            # Tier 1: Structured data extraction (moderate complexity)
            if tier == 'tier1':
                if spec.tier == ModelTier.STANDARD:
                    score += 0.3  # Standard is perfect for structured extraction
                elif spec.tier == ModelTier.PREMIUM:
                    score += 0.2  # Premium works but may be overkill
                elif spec.tier == ModelTier.LITE:
                    score += 0.1  # Lite can handle structured data

            # Tier 2: Nuanced reasoning (stress, red flags, implicit requirements)
            # Requires better reasoning than Tier 1
            elif tier == 'tier2':
                if spec.tier == ModelTier.PREMIUM:
                    score += 0.4  # Premium best for nuanced analysis
                elif spec.tier == ModelTier.STANDARD:
                    score += 0.3  # Standard works well
                elif spec.tier == ModelTier.LITE:
                    score -= 0.2  # Lite may miss subtle patterns

            # Tier 3: Strategic thinking (prestige, positioning, pain points)
            # Requires most sophisticated reasoning
            elif tier == 'tier3':
                if spec.tier == ModelTier.PREMIUM:
                    score += 0.5  # Premium essential for strategic analysis
                elif spec.tier == ModelTier.STANDARD:
                    score += 0.2  # Standard acceptable but not ideal
                elif spec.tier == ModelTier.LITE:
                    score -= 0.3  # Lite insufficient for strategic thinking

            # Large batches prefer higher capacity models
            if batch_size > 15:
                if spec.tier in [ModelTier.STANDARD, ModelTier.PREMIUM]:
                    score += 0.2
                else:
                    score -= 0.1

            # Small batches can use any model (batch size less relevant for quality)
            elif batch_size < 5:
                # Don't penalize or reward based solely on batch size for small batches
                pass

            scores[model_id] = max(0.0, min(1.0, score))

        return scores

    def _score_by_budget(self, tokens_used: int, token_limit: int) -> Dict[str, float]:
        """
        Score models based on token budget remaining.

        Args:
            tokens_used: Tokens used today
            token_limit: Daily token limit

        Returns:
            Dict of {model_id: score}
        """
        usage_ratio = tokens_used / token_limit if token_limit > 0 else 0
        scores = {}

        for model_id, spec in self.MODELS.items():
            score = 0.5

            # Critical budget situation (>90%)
            if usage_ratio > self.BUDGET_THRESHOLDS['critical']:
                if spec.tier == ModelTier.LITE:
                    score += 0.4  # Strongly prefer lite
                else:
                    score -= 0.3  # Avoid others

            # High usage (80-90%)
            elif usage_ratio > self.BUDGET_THRESHOLDS['high']:
                if spec.tier == ModelTier.LITE:
                    score += 0.3
                elif spec.tier == ModelTier.STANDARD:
                    score += 0.1
                else:
                    score -= 0.2

            # Moderate usage (60-80%)
            elif usage_ratio > self.BUDGET_THRESHOLDS['moderate']:
                if spec.tier == ModelTier.STANDARD:
                    score += 0.2  # Prefer balanced
                elif spec.tier == ModelTier.LITE:
                    score += 0.1
                else:
                    score -= 0.1

            # Low usage (<60%)
            else:
                if spec.tier == ModelTier.PREMIUM:
                    score += 0.3  # Can afford premium
                elif spec.tier == ModelTier.STANDARD:
                    score += 0.2
                # Lite gets baseline (0.5)

            scores[model_id] = max(0.0, min(1.0, score))

        return scores

    def _score_by_quality(
        self,
        recent_quality: Optional[float],
        tier: str
    ) -> Dict[str, float]:
        """
        Score models based on recent quality metrics.

        Args:
            recent_quality: Recent quality score (0.0-1.0), None if no data
            tier: Current analysis tier

        Returns:
            Dict of {model_id: score}
        """
        scores = {}

        for model_id, spec in self.MODELS.items():
            score = 0.5

            if recent_quality is None:
                # No quality data, use tier-based defaults
                if tier == 'tier1':
                    # Tier 1 needs high quality
                    if spec.tier in [ModelTier.STANDARD, ModelTier.PREMIUM]:
                        score += 0.2
                else:
                    # Tier 2/3 less critical
                    score += 0.1

            elif recent_quality < self.QUALITY_THRESHOLDS['low']:
                # Low quality - need upgrade
                if spec.tier == ModelTier.PREMIUM:
                    score += 0.4
                elif spec.tier == ModelTier.STANDARD:
                    score += 0.2
                else:
                    score -= 0.3  # Avoid lite

            elif recent_quality < self.QUALITY_THRESHOLDS['acceptable']:
                # Below acceptable - prefer standard or premium
                if spec.tier in [ModelTier.STANDARD, ModelTier.PREMIUM]:
                    score += 0.3
                else:
                    score -= 0.1

            elif recent_quality > self.QUALITY_THRESHOLDS['excellent']:
                # Excellent quality - can try lighter model for savings
                if spec.tier == ModelTier.LITE:
                    score += 0.2
                else:
                    score += 0.1  # Others acceptable

            else:
                # Acceptable quality - maintain current tier
                score += 0.1

            scores[model_id] = max(0.0, min(1.0, score))

        return scores

    def _score_by_time(self, time_sensitive: bool) -> Dict[str, float]:
        """
        Score models based on time sensitivity and time of day.

        Args:
            time_sensitive: Whether fast response is critical

        Returns:
            Dict of {model_id: score}
        """
        scores = {}
        current_hour = datetime.now().hour
        is_peak_hours = 9 <= current_hour <= 17

        for model_id, spec in self.MODELS.items():
            score = 0.5

            if time_sensitive:
                # Time-sensitive requests prefer faster models
                if spec.tier == ModelTier.LITE:
                    score += 0.3  # Fastest
                elif spec.tier == ModelTier.PREMIUM:
                    score += 0.2  # Also fast
                else:
                    score += 0.1  # Standard is okay

            # Peak hours strategy: conserve with lite model
            if is_peak_hours:
                if spec.tier == ModelTier.LITE:
                    score += 0.2
                else:
                    score -= 0.1

            # Off-peak hours: can use better models
            else:
                if spec.tier in [ModelTier.STANDARD, ModelTier.PREMIUM]:
                    score += 0.2

            scores[model_id] = max(0.0, min(1.0, score))

        return scores

    def _build_selection_reason(
        self,
        model_id: str,
        tier: str,
        batch_size: int,
        usage_ratio: float,
        quality: Optional[float],
        time_sensitive: bool
    ) -> str:
        """Build human-readable selection rationale."""
        model_spec = self.MODELS[model_id]
        reasons = []

        # Workload reason
        if tier == 'tier1' and batch_size > 10:
            reasons.append(f"Complex Tier 1 analysis with large batch ({batch_size} jobs)")
        elif tier in ['tier2', 'tier3']:
            reasons.append(f"{tier.capitalize()} analysis (lighter workload)")

        # Budget reason
        if usage_ratio > 0.9:
            reasons.append(f"High token usage ({usage_ratio:.0%}), conserving with {model_spec.tier.value} model")
        elif usage_ratio < 0.4:
            reasons.append(f"Low token usage ({usage_ratio:.0%}), using {model_spec.tier.value} model")

        # Quality reason
        if quality is not None:
            if quality < 0.75:
                reasons.append(f"Low recent quality ({quality:.0%}), upgrading to {model_spec.tier.value}")
            elif quality > 0.95:
                reasons.append(f"Excellent quality ({quality:.0%}), maintaining {model_spec.tier.value}")

        # Time reason
        if time_sensitive:
            reasons.append("Time-sensitive request")

        return "; ".join(reasons) if reasons else f"Default selection for {tier}"

    def _estimate_cost(self, model_spec: ModelSpec, batch_size: int, tier: str) -> float:
        """Estimate cost for this analysis."""
        # Simplified cost estimation
        tokens_per_job = {'tier1': 2000, 'tier2': 1500, 'tier3': 1200}.get(tier, 2000)
        total_tokens = batch_size * tokens_per_job

        input_cost = (total_tokens / 1000) * model_spec.input_cost_per_1k
        output_cost = (total_tokens / 1000) * model_spec.output_cost_per_1k

        return input_cost + output_cost

    def _estimate_quality(self, model_spec: ModelSpec, tier: str) -> float:
        """
        Estimate expected quality for this model/tier combination.

        Quality expectations by tier:
        - Tier 1: Structured data extraction (JSON parsing, field extraction)
                  Even lite models can achieve good quality with clear schemas
        - Tier 2: Nuanced reasoning (detecting stress indicators, red flags)
                  Requires better reasoning - quality gap widens
        - Tier 3: Strategic thinking (prestige assessment, positioning advice)
                  Highest reasoning demands - premium models shine here
        """
        # Quality estimates based on model tier and analysis tier
        quality_matrix = {
            # Tier 1: Structured extraction - all models reasonably capable
            (ModelTier.LITE, 'tier1'): 0.85,      # Lite decent for structured data
            (ModelTier.STANDARD, 'tier1'): 0.92,  # Standard very good
            (ModelTier.PREMIUM, 'tier1'): 0.95,   # Premium excellent but diminishing returns

            # Tier 2: Nuanced reasoning - quality gap widens
            (ModelTier.LITE, 'tier2'): 0.75,      # Lite struggles with nuance
            (ModelTier.STANDARD, 'tier2'): 0.88,  # Standard good for nuanced analysis
            (ModelTier.PREMIUM, 'tier2'): 0.96,   # Premium excels at detecting patterns

            # Tier 3: Strategic thinking - premium essential
            (ModelTier.LITE, 'tier3'): 0.65,      # Lite insufficient for strategic thinking
            (ModelTier.STANDARD, 'tier3'): 0.82,  # Standard acceptable but limited
            (ModelTier.PREMIUM, 'tier3'): 0.97,   # Premium necessary for strategic insights
        }

        return quality_matrix.get((model_spec.tier, tier), 0.85)

    def get_model_stats(self) -> Dict:
        """Get statistics about model usage."""
        return {
            'current_model': self.current_model,
            'default_model': self.default_model,
            'total_switches': self.model_switches,
            'selection_count': len(self.selection_history),
            'recent_selections': self.selection_history[-10:] if self.selection_history else [],
        }
