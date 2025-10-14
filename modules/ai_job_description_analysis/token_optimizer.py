"""
Token Optimizer - Dynamic Output Token Management
=================================================

Calculates optimal max_output_tokens based on job count, prompt complexity,
and analysis tier to minimize costs while ensuring complete responses.

Features:
- Dynamic token calculation based on job count
- Tier-aware token allocation
- Safety margins to prevent truncation
- Cost estimation and optimization
- Batch size recommendations

Author: Automated Job Application System v4.3.2
Created: 2025-10-12
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TokenAllocation:
    """
    Token allocation result with breakdown and recommendations.
    """
    max_output_tokens: int
    estimated_tokens_per_job: int
    safety_margin: float
    tier: str
    job_count: int
    cost_estimate: float
    recommendations: List[str]


class TokenOptimizer:
    """
    Optimizes token allocation for Gemini API calls based on workload.

    This class calculates the optimal max_output_tokens parameter for different
    analysis tiers and job counts to minimize costs while ensuring complete responses.
    """

    # Token allocation per job by tier (empirically determined)
    TOKENS_PER_JOB = {
        'tier1': {
            'base': 150,        # Base tokens for job metadata
            'skills': 200,      # Skills analysis (5-35 skills)
            'authenticity': 50, # Authenticity check
            'classification': 50,  # Industry classification
            'structured_data': 350,  # Work arrangement, compensation, etc.
            'total': 800        # Total per job for Tier 1
        },
        'tier2': {
            'base': 100,
            'stress_analysis': 150,
            'red_flags': 200,
            'implicit_requirements': 150,
            'total': 600        # Total per job for Tier 2
        },
        'tier3': {
            'base': 100,
            'prestige_analysis': 300,
            'cover_letter_insights': 200,
            'total': 600        # Total per job for Tier 3
        }
    }

    # Safety margins by tier (to prevent truncation)
    SAFETY_MARGINS = {
        'tier1': 1.3,  # 30% safety margin (complex structured data)
        'tier2': 1.2,  # 20% safety margin (narrative analysis)
        'tier3': 1.2,  # 20% safety margin (strategic insights)
    }

    # Gemini model limits
    MAX_OUTPUT_TOKENS_LIMIT = 8192  # Gemini 2.0 Flash limit

    # Cost per 1K tokens (for paid tier reference)
    COST_PER_1K_OUTPUT = 0.60  # $0.60 per 1M tokens = $0.0006 per 1K

    def __init__(self):
        """Initialize the token optimizer."""
        logger.info("TokenOptimizer initialized")

    def calculate_optimal_tokens(
        self,
        job_count: int,
        tier: str = 'tier1',
        custom_safety_margin: Optional[float] = None
    ) -> TokenAllocation:
        """
        Calculate optimal max_output_tokens for a batch analysis.

        Args:
            job_count: Number of jobs in the batch
            tier: Analysis tier ('tier1', 'tier2', 'tier3')
            custom_safety_margin: Override default safety margin (1.0 = no margin)

        Returns:
            TokenAllocation with optimal settings and recommendations
        """
        if tier not in self.TOKENS_PER_JOB:
            logger.warning(f"Unknown tier '{tier}', defaulting to tier1")
            tier = 'tier1'

        # Get base tokens per job for this tier
        base_tokens_per_job = self.TOKENS_PER_JOB[tier]['total']

        # Calculate estimated tokens needed
        estimated_tokens = job_count * base_tokens_per_job

        # Apply safety margin
        safety_margin = custom_safety_margin or self.SAFETY_MARGINS[tier]
        tokens_with_margin = int(estimated_tokens * safety_margin)

        # Add overhead for JSON structure (100 tokens for wrapper)
        json_overhead = 100
        total_tokens = tokens_with_margin + json_overhead

        # Cap at model limit
        max_output_tokens = min(total_tokens, self.MAX_OUTPUT_TOKENS_LIMIT)

        # Calculate cost estimate
        cost_estimate = (max_output_tokens / 1000) * self.COST_PER_1K_OUTPUT

        # Generate recommendations
        recommendations = self._generate_recommendations(
            job_count,
            tier,
            max_output_tokens,
            estimated_tokens
        )

        allocation = TokenAllocation(
            max_output_tokens=max_output_tokens,
            estimated_tokens_per_job=base_tokens_per_job,
            safety_margin=safety_margin,
            tier=tier,
            job_count=job_count,
            cost_estimate=cost_estimate,
            recommendations=recommendations
        )

        logger.info(
            f"Token allocation for {job_count} jobs ({tier}): "
            f"{max_output_tokens} tokens (estimated: {estimated_tokens}, "
            f"safety margin: {safety_margin:.1%})"
        )

        return allocation

    def _generate_recommendations(
        self,
        job_count: int,
        tier: str,
        max_output_tokens: int,
        estimated_tokens: int
    ) -> List[str]:
        """
        Generate optimization recommendations based on allocation.

        Args:
            job_count: Number of jobs
            tier: Analysis tier
            max_output_tokens: Calculated max tokens
            estimated_tokens: Estimated tokens needed

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Check if we're at the limit
        if max_output_tokens >= self.MAX_OUTPUT_TOKENS_LIMIT:
            recommendations.append(
                f"⚠️ At token limit ({self.MAX_OUTPUT_TOKENS_LIMIT}). "
                f"Consider reducing batch size from {job_count} to {self._calculate_max_batch_size(tier)} jobs."
            )

        # Suggest batch size adjustments
        optimal_batch_size = self._calculate_optimal_batch_size(tier)
        if job_count > optimal_batch_size:
            recommendations.append(
                f"💡 Optimal batch size for {tier} is {optimal_batch_size} jobs. "
                f"Current: {job_count}. Consider splitting into multiple batches."
            )

        # Check token efficiency
        utilization = (estimated_tokens / max_output_tokens) * 100
        if utilization < 60:
            recommendations.append(
                f"💰 Token utilization only {utilization:.1f}%. "
                f"You could fit {int((max_output_tokens - 100) / self.TOKENS_PER_JOB[tier]['total'])} jobs "
                f"in this allocation for better efficiency."
            )

        # Cost optimization suggestion
        if tier == 'tier1' and job_count < 5:
            recommendations.append(
                "💡 For small batches (<5 jobs), consider combining multiple batches "
                "to reduce API call overhead and improve cost efficiency."
            )

        return recommendations

    def _calculate_max_batch_size(self, tier: str) -> int:
        """
        Calculate maximum batch size that fits within token limit.

        Args:
            tier: Analysis tier

        Returns:
            Maximum number of jobs that can fit in one batch
        """
        tokens_per_job = self.TOKENS_PER_JOB[tier]['total']
        safety_margin = self.SAFETY_MARGINS[tier]
        json_overhead = 100

        # Work backwards from limit
        available_tokens = self.MAX_OUTPUT_TOKENS_LIMIT - json_overhead
        max_jobs = int(available_tokens / (tokens_per_job * safety_margin))

        return max(1, max_jobs)  # At least 1 job

    def _calculate_optimal_batch_size(self, tier: str) -> int:
        """
        Calculate optimal batch size for cost-efficiency.

        This balances between:
        - API call overhead (favor larger batches)
        - Token efficiency (avoid over-allocation)
        - Processing time (reasonable batch sizes)

        Args:
            tier: Analysis tier

        Returns:
            Optimal number of jobs per batch
        """
        # Optimal batch sizes empirically determined
        optimal_sizes = {
            'tier1': 10,  # Tier 1: Most complex, moderate batches
            'tier2': 15,  # Tier 2: Lighter, can handle more
            'tier3': 15,  # Tier 3: Similar to Tier 2
        }

        return optimal_sizes.get(tier, 10)

    def estimate_total_cost(
        self,
        total_jobs: int,
        tier: str = 'tier1',
        include_input_tokens: bool = True
    ) -> Dict:
        """
        Estimate total cost for analyzing a set of jobs.

        Args:
            total_jobs: Total number of jobs to analyze
            tier: Analysis tier
            include_input_tokens: Include input token costs (default: True)

        Returns:
            Dict with cost breakdown
        """
        optimal_batch_size = self._calculate_optimal_batch_size(tier)
        num_batches = (total_jobs + optimal_batch_size - 1) // optimal_batch_size

        # Calculate per-batch costs
        allocation = self.calculate_optimal_tokens(optimal_batch_size, tier)
        output_cost_per_batch = allocation.cost_estimate

        # Estimate input tokens (prompt + job descriptions)
        avg_job_description_tokens = 500  # Average job description length
        prompt_overhead = 1000  # Security tokens, instructions, JSON schema
        input_tokens_per_batch = (optimal_batch_size * avg_job_description_tokens) + prompt_overhead
        input_cost_per_batch = (input_tokens_per_batch / 1000) * 0.30  # $0.30 per 1M input tokens

        total_output_cost = output_cost_per_batch * num_batches
        total_input_cost = input_cost_per_batch * num_batches if include_input_tokens else 0
        total_cost = total_output_cost + total_input_cost

        return {
            'total_jobs': total_jobs,
            'tier': tier,
            'optimal_batch_size': optimal_batch_size,
            'num_batches': num_batches,
            'output_tokens_per_batch': allocation.max_output_tokens,
            'input_tokens_per_batch': input_tokens_per_batch,
            'output_cost_per_batch': output_cost_per_batch,
            'input_cost_per_batch': input_cost_per_batch,
            'total_output_cost': total_output_cost,
            'total_input_cost': total_input_cost,
            'total_cost': total_cost,
            'cost_per_job': total_cost / total_jobs if total_jobs > 0 else 0,
        }

    def get_token_breakdown(self, tier: str) -> Dict:
        """
        Get detailed token breakdown for a tier.

        Args:
            tier: Analysis tier

        Returns:
            Dict with token allocation by section
        """
        if tier not in self.TOKENS_PER_JOB:
            logger.warning(f"Unknown tier '{tier}'")
            return {}

        breakdown = self.TOKENS_PER_JOB[tier].copy()
        breakdown['tier'] = tier
        breakdown['safety_margin'] = self.SAFETY_MARGINS[tier]
        breakdown['tokens_with_margin'] = int(breakdown['total'] * breakdown['safety_margin'])

        return breakdown
